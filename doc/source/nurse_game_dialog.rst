
Dialogs in The Nurse Project
*****************************

.. note::
        22/05/2011

The ``main()`` function may instanciate a :class:`nurse.game.dialog.DialogContext` 
which is added to a list of contexts managed by the :class:`nurse.context.ContextManager`.
The :class:`nurse.game.DialogContext` ``__init__()`` function instanciates various 
sprites (such as :class:`nurse.sprite.UniformLayer`), a :class:`nurse.sprite.Dialog` 
(:class:`nurse.sprite.Sprite` (:class:`nurse.state_machine.StateMachine`) ) and a
:class:`nurse.game.dialog.DialogListener`.

As a :class:`nurse.sprite.Sprite` and therefore a :class:`nurse.state_machine.StateMachine`,
the :class:`nurse.sprite.Dialog` has a member ``states`` which is a list of 
:class:`nurse.game.dialog.DialogState` (:class:`nurse.state_machine.State`). 
The :func:`nurse.sprite.Dialog.update` function actually just calls the 
:func:`nurse.game.dialog.DialogState.update` function of the :class:`nurse.game.dialog.DialogState`
defined by the member ``_current_state`` of the :class:`nurse.sprite.Dialog`.

For each :class:`nurse.sprite.Sprite` and in particular for the :class:`nurse.sprite.Dialog`,
the method :func:`nurse.state_machine.StateMachine.start` is called, which initializes
the member ``_current_state`` with ``_initial_state``, should it be previously defined 
by the method :func:`nurse.state_machine.StateMachine.set_initial_state` or by a 
default instance created in that same :func:`nurse.state_machine.StateMachine.start`
function. Then the :class:`nurse.context.ContextManager` updates its :class:`nurse.context.Context`,
or more specifically each :class:`nurse.context.Context` has its :class:`nurse.state_machine.StateMachine`
updated. With regard to this, the :class:`nurse.game.dialog.DialogContext` updates its sprites,
therefore the :class:`nurse.sprite.Dialog` and its current :class:`nurse.game.dialog.DialogState`.

:mod:`nurse.game.dialog`
=========================

.. automodule:: nurse.game.dialog
   :members:
   :undoc-members:
   :inherited-members:
