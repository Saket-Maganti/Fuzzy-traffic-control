import numpy as np
import skfuzzy as fuzz
from src.Config import Config


class Fuzzy:
    def __init__(self):
        """Initialize membership functions for fuzzy logic controller."""
        # Load fuzzy ranges
        rng = Config['fuzzy']['range']
        self.x_behind_red_light = rng['behind_red_light']
        self.x_arriving_green_light = rng['arriving_green_light']
        self.x_extension = rng['extension']

        # Membership functions for arriving cars
        mf = Config['fuzzy']['membership_function']['arriving_green_light']
        self.arriving = {
            'few': fuzz.trimf(self.x_arriving_green_light, mf['few']),
            'small': fuzz.trimf(self.x_arriving_green_light, mf['small']),
            'medium': fuzz.trimf(self.x_arriving_green_light, mf['medium']),
            'many': fuzz.trimf(self.x_arriving_green_light, mf['many'])
        }

        # Membership functions for queue behind red light
        mf = Config['fuzzy']['membership_function']['behind_red_light']
        self.behind = {
            'few': fuzz.trimf(self.x_behind_red_light, mf['few']),
            'small': fuzz.trimf(self.x_behind_red_light, mf['small']),
            'medium': fuzz.trimf(self.x_behind_red_light, mf['medium']),
            'many': fuzz.trimf(self.x_behind_red_light, mf['many'])
        }

        # Membership functions for extension decision
        mf = Config['fuzzy']['membership_function']['extension']
        self.extension_mfs = {
            'zero': fuzz.trimf(self.x_extension, mf['zero']),
            'short': fuzz.trimf(self.x_extension, mf['short']),
            'medium': fuzz.trimf(self.x_extension, mf['medium']),
            'long': fuzz.trimf(self.x_extension, mf['long'])
        }

    def _fuzzify(self, arriving_val, behind_val):
        """Fuzzify crisp inputs to degrees of membership."""
        arriving_levels = {
            k: fuzz.interp_membership(self.x_arriving_green_light, v, arriving_val)
            for k, v in self.arriving.items()
        }
        behind_levels = {
            k: fuzz.interp_membership(self.x_behind_red_light, v, behind_val)
            for k, v in self.behind.items()
        }
        return arriving_levels, behind_levels

    def _evaluate_rules(self, arriving, behind, extension_count):
        """Evaluate fuzzy rules and return aggregated membership output."""

        # Define fuzzy rules
        rule = {}
        rule['r1'] = arriving['few']
        rule['r2'] = np.fmin(arriving['small'], np.fmax(behind['few'], behind['small']))
        rule['r3'] = np.fmin(arriving['small'], np.fmax(behind['medium'], behind['many']))
        rule['r4'] = np.fmin(arriving['medium'], np.fmax(behind['few'], behind['small']))
        rule['r5'] = np.fmin(arriving['medium'], np.fmax(behind['medium'], behind['many']))
        rule['r6'] = np.fmin(arriving['many'], behind['few'])
        rule['r7'] = np.fmin(arriving['many'], np.fmax(behind['small'], behind['medium']))
        rule['r8'] = np.fmin(arriving['many'], behind['many'])

        if extension_count == 0:
            activations = {
                'zero': np.fmax(rule['r1'], rule['r3']),
                'short': np.fmax(rule['r2'], np.fmax(rule['r5'], rule['r8'])),
                'medium': np.fmax(rule['r4'], rule['r7']),
                'long': rule['r6']
            }
        else:
            activations = {
                'zero': np.fmax(rule['r1'], np.fmax(rule['r2'], np.fmax(rule['r3'], np.fmax(rule['r5'], rule['r8'])))),
                'short': np.fmax(rule['r4'], rule['r7']),
                'medium': rule['r6'],
                'long': 0  # no further extension after first
            }

        # Apply rule activation to output membership functions
        fuzzy_output = np.fmax.reduce([
            np.fmin(activations['zero'], self.extension_mfs['zero']),
            np.fmin(activations['short'], self.extension_mfs['short']),
            np.fmin(activations['medium'], self.extension_mfs['medium']),
            np.fmin(activations['long'], self.extension_mfs['long'])
        ])

        return fuzzy_output

    def get_extension(self, arriving_green_light_car, behind_red_light_car, extension_count):
        """
        Perform fuzzy inference and defuzzify output to get extension time.
        :param arriving_green_light_car: Number of cars approaching green light
        :param behind_red_light_car: Number of cars waiting behind red light
        :param extension_count: 0 for first-time extension, 1+ for subsequent rounds
        :return: crisp extension value (seconds)
        """
        arriving_levels, behind_levels = self._fuzzify(arriving_green_light_car, behind_red_light_car)
        fuzzy_result = self._evaluate_rules(arriving_levels, behind_levels, extension_count)
        return fuzz.defuzz(self.x_extension, fuzzy_result, 'centroid')
