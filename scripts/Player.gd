extends CharacterBody2D

@export var move_speed: float = 200.0
@onready var interaction_area: Area2D = $InteractionArea

var last_move: Vector2 = Vector2.RIGHT
var hovered_target: Node = null

func _ready() -> void:
	interaction_area.body_entered.connect(_on_InteractionArea_body_entered)
	interaction_area.body_exited.connect(_on_InteractionArea_body_exited)

func _physics_process(delta: float) -> void:
	var input_vector := Vector2.ZERO
	input_vector.y = Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	input_vector.x = Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left")
	input_vector = input_vector.normalized()
	velocity = input_vector * move_speed
	if input_vector.length() > 0.1:
		last_move = input_vector
	move_and_slide()

func _process(_delta: float) -> void:
	if Input.is_action_just_pressed("interact") and hovered_target:
		if hovered_target.has_method("on_interact"):
			hovered_target.on_interact(get_parent())

func _on_InteractionArea_body_entered(body: Node) -> void:
	if body.is_in_group("interactable"):
		hovered_target = body
		get_parent().show_interaction_prompt(body)

func _on_InteractionArea_body_exited(body: Node) -> void:
	if hovered_target == body:
		hovered_target = null
		get_parent().hide_interaction_prompt()
