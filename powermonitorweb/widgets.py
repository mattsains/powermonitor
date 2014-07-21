from django import forms
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from itertools import chain

class EnabledSelect(forms.Select):
    def __init__(self, enabled_choice_list=None, *args, **kwargs):
        """
        A custom Select widget that takes an additional list of values (IDs) of all items that are considered "enabled".
        The option tags for these will be given an attribute called "data-enabled" to reflect that.
        """
        super(EnabledSelect, self).__init__(*args, **kwargs)
        self.enabled_choices = enabled_choice_list

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(format_html('<optgroup label="{0}">', force_text(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, self.enabled_choices, *option))
                output.append('</optgroup>')
            else:
                output.append(self.render_option(selected_choices, self.enabled_choices, option_value, option_label))
        return '\n'.join(output)
    
    def render_option(self, selected_choices, enabled_choices, option_value, option_label):
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''

        if int(option_value) in enabled_choices:
            enabled_html = mark_safe(' data-enabled="true"')
        else:
            enabled_html = ''
        return format_html('<option value="{0}"{1}{2}>{3}</option>',
                           option_value,
                           selected_html,
                           enabled_html,
                           force_text(option_label))
