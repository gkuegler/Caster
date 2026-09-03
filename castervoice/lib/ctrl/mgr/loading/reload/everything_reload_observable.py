from dragonfly import Function, MappingRule, Key

from castervoice.lib.ctrl.mgr.loading.reload.base_reload_observable import (
    BaseReloadObservable,
)
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

from time import sleep

try:
    from natlink import setMicState
except:
    setMicState = lambda x: None

toast_is_loaded = False
try:
    from library import notify
    toast_is_loaded = True
except:
    pass

class Listener:
    def __init__(self):
        self.reloaded_files = []

    def receive(self, path_changed):
        self.reloaded_files.append(path_changed)

    def reset(self):
        self.reloaded_files = []

    def notify_user(self):
        # msg = "caster" if self.reloaded_files else "nothing"
        if toast_is_loaded:
            notify.toast("\n".join(self.reloaded_files) if self.reloaded_files else "nothing", "Reloaded Caster Rules")


class ManualReloadObservable(BaseReloadObservable):
    """
    Allows for reloading changed files on command.
    """

    def __init__(self):
        super(ManualReloadObservable, self).__init__()

        """
        This class itself will never be reloaded, but it can
        be registered like the other rules and so can have
        transformers run over it, etc.
        """

        class ManualGrammarReloadRule(MappingRule):
            mapping = {
                "reload all rules": Function(self.reload_all_rules),
                "rejuvenate": Function(self.reload_everything),
            }

        self._rule_class = ManualGrammarReloadRule
        self.listener = Listener()
        self.register_listener(self.listener)

    def reload_all_rules(self):
        self.listener.reset()
        self._update()
        self.listener.notify_user()

    def reload_everything(self):
        """
        Reload Caster as well as dragonfly rules. Dragonfly rules are reloaded
        by cycling the microphone.
        """
        # Save the current file
        Key("c-s/30").execute()

        # Cycle microphone to reload dragonfly rules.
        setMicState("off")
        sleep(0.2)
        setMicState("on")
        
        # Reload Caster rules.
        self.reload_all_rules()

    def get_loadable(self):
        details = RuleDetails(
            name="caster manual grammars reload command rule", watch_exclusion=True
        )
        return self._rule_class, details
