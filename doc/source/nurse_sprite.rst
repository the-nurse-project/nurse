
Sprites in :doc:`The Nurse Project <index>` 
***************************************************

The module :mod:`nurse.sprite` contains various classes for sprites creation
and display. 

The main class :class:`nurse.sprite.Sprite` derives from :class:`nurse.state_machine.StateMachine`.

Here is a list of classes derived from class :class:`nurse.sprite.Sprite` :

  - :class:`nurse.sprite.Player`
  - :class:`nurse.sprite.MovingSprite`
  - :class:`nurse.sprite.StaticSprite`
  - :class:`nurse.sprite.Text`
  - :class:`nurse.sprite.FpsSprite`
  - :class:`nurse.sprite.Dialog`
  - :class:`nurse.sprite.UniformLayer`

.. code-block:: python

        sprite = StaticSprite('dialog', context, layer=0, imgname='dialog.png')
        sprite.set_location([100, 100])
        sprite.start()

:mod:`nurse.sprite`
==========================

.. automodule:: nurse.sprite
    :members:
    :undoc-members:
    :inherited-members:


