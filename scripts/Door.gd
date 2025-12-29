extends Area2D

@export var target_room: String = ""
@export var price: int = 400
@export var room_id: String = ""
@export var locked: bool = true

@onready var rect: ColorRect = $ColorRect
@onready var label: Label = $Label

func _ready() -> void:
	add_to_group("interactable")
	update_visuals()

func update_visuals() -> void:
	if locked:
		rect.color = Color(0.78, 0.31, 0.31, 1)
		label.text = "Purchase Room (%d cr)" % price
	else:
		rect.color = Color(0.31, 0.78, 0.47, 1)
		label.text = "Enter"

func on_interact(game) -> void:
	game.handle_door_interaction(self)
