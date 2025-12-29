extends Node2D

@export var room_id: String = "Room_01"
@export var spawn_position: Vector2 = Vector2.ZERO

@onready var incubators_parent: Node = $Incubators
@onready var door: Area2D = $Door if has_node("Door") else null

var game_ref: Node = null

func configure(game) -> void:
	game_ref = game
	for inc in get_incubators():
		inc.add_to_group("incubator")

func get_incubators() -> Array:
	return incubators_parent.get_children()

func get_spawn_position() -> Vector2:
	return spawn_position
