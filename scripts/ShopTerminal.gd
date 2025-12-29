extends Area2D

func _ready() -> void:
	add_to_group("interactable")
	# ColorRect visual defined in scene

func on_interact(game) -> void:
	game.open_shop()
