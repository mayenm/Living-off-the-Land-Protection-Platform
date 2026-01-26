import yaml
import os
import logging
import re

class SigmaRule:
    def __init__(self, rule_path):
        self.path = rule_path
        self.raw = {}
        self.title = ""
        self.id = ""
        self.level = "low"
        self.detection = {}
        self.valid = False
        self._load()

    def _load(self):
        try:
            with open(self.path, 'r') as f:
                self.raw = yaml.safe_load(f)
                self.title = self.raw.get("title", f"Unknown Rule {os.path.basename(self.path)}")
                self.id = self.raw.get("id", "")
                self.level = self.raw.get("level", "low")
                self.detection = self.raw.get("detection", {})
                self.valid = True
        except Exception as e:
            logging.error(f"Failed to load sigma rule {self.path}: {e}")
            self.valid = False

    def match(self, event_dict):
        """
        Check if event_dict matches the Sigma rule.
        Supports basic boolean logic in 'condition'.
        """
        if not self.valid:
            return False

        condition = self.detection.get("condition", "")
        if not condition:
            return False

        # Map of selection names to their boolean results
        results = {}
        for key, value in self.detection.items():
            if key == "condition":
                continue
            results[key] = self._check_selection(value, event_dict)

        # Basic condition parser (handles simple cases like 'selection', '1 of selection*', 'selection1 and not selection2')
        try:
            return self._test_condition(condition, results)
        except Exception as e:
            logging.debug(f"Condition evaluation failed for {self.title}: {e}")
            # Fallback for simple single selection
            if condition in results:
                return results[condition]
            return False

    def _test_condition(self, condition, results):
        """
        Very simplified condition evaluator.
        Supports 'selection', 'selection1 and selection2', 'selection1 or selection2', 'not selection'.
        """
        # Replace selection names with their results
        # We sort by length descending to avoid partial replacement issues (e.g. 'sel' vs 'selection')
        for selection_name in sorted(results.keys(), key=len, reverse=True):
            condition = condition.replace(selection_name, str(results[selection_name]))
        
        # Clean up Sigma specific terms
        condition = condition.replace(" and ", " and ") # already python compatible
        condition = condition.replace(" or ", " or ")
        condition = condition.replace(" not ", " not ")
        
        # Handle '1 of ...' or 'all of ...' - VERY BASIC
        if "1 of " in condition:
            # If any of the results are True, return True
            return any(results.values())
        if "all of " in condition:
            return all(results.values())

        # Evaluate as Python expression
        try:
            # Dangerous if rules are untrusted, but usually Sigma rules are safe.
            # We restrict globals/locals to be safe.
            return eval(condition, {"__builtins__": {}}, {"True": True, "False": False})
        except:
            return False

    def _check_selection(self, selection, event_dict):
        """
        selection can be a dict (AND logic) or a list (OR logic)
        """
        if isinstance(selection, list):
            # List in Sigma means OR logic between items
            return any(self._check_selection(item, event_dict) for item in selection)
        
        if not isinstance(selection, dict):
            return False

        # Dict in Sigma means AND logic between fields
        for field_modifier, value in selection.items():
            parts = field_modifier.split('|')
            field = parts[0]
            modifier = parts[1] if len(parts) > 1 else "exact"
            
            mapping = {
                "Image": "image",
                "CommandLine": "command_line",
                "ParentImage": "parent_image",
                "ParentCommandLine": "parent_command_line",
                "User": "user",
                "ProcessId": "pid"
            }
            mapped_key = mapping.get(field, field.lower())
            event_val = event_dict.get(mapped_key, "")

            if not self._check_value(event_val, value, modifier):
                return False
        
        return True

    def _check_value(self, event_val, rule_val, modifier):
        if event_val is None:
            event_val = ""
            
        event_val = str(event_val).lower()
        
        if isinstance(rule_val, list):
            # List of values in a field means OR logic
            return any(self._check_single_value(event_val, v, modifier) for v in rule_val)
        else:
            return self._check_single_value(event_val, rule_val, modifier)

    def _check_single_value(self, event_val, rule_val, modifier):
        if rule_val is None:
            return False
            
        rule_val = str(rule_val).lower()
        
        if modifier == "contains":
            return rule_val in event_val
        elif modifier == "startswith":
            return event_val.startswith(rule_val)
        elif modifier == "endswith":
            return event_val.endswith(rule_val)
        elif modifier == "exact":
            return event_val == rule_val
        elif modifier == "re":
            try:
                return re.search(rule_val, event_val) is not None
            except:
                return False
        return False


class DetectionEngine:
    def __init__(self, rules_dir):
        self.rules_dir = rules_dir
        self.rules = []
        self.load_rules()

    def load_rules(self):
        self.rules = []
        if not os.path.exists(self.rules_dir):
            logging.warning(f"Rules directory {self.rules_dir} does not exist.")
            return

        for f in os.listdir(self.rules_dir):
            if f.endswith(".yml") or f.endswith(".yaml"):
                rule = SigmaRule(os.path.join(self.rules_dir, f))
                if rule.valid:
                    self.rules.append(rule)
        logging.info(f"Loaded {len(self.rules)} Sigma rules.")

    def evaluate(self, event_obj):
        """
        Evaluate an event against all loaded rules.
        Returns a list of matching rules.
        """
        matches = []
        event_dict = event_obj.to_dict()
        
        for rule in self.rules:
            if rule.match(event_dict):
                matches.append(rule)
        
        return matches
