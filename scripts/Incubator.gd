extends Area2D

enum State { EMPTY, GROWING, READY }

@export var incubator_id: String = ""
@export var growth_stage_count: int = 3

var state: State = State.EMPTY
var seed_id: String = ""
var start_time: float = 0.0
var grow_duration: float = 0.0

@onready var base_rect: ColorRect = $Base
@onready var progress_bar: ColorRect = $ProgressBar/Fill
@onready var stage_label: Label = $StageLabel

func _ready() -> void:
	add_to_group("interactable")
	update_visuals()

func _process(delta: float) -> void:
	if state == State.GROWING:
		var elapsed := Time.get_unix_time_from_system() - start_time
		var t := clamp(elapsed / grow_duration, 0.0, 1.0)
		progress_bar.scale.x = t
		var stage := int(t * growth_stage_count)
		stage_label.text = "Stage %d/%d" % [stage + 1, growth_stage_count]
		if elapsed >= grow_duration:
			state = State.READY
			stage_label.text = "Ready!"
			progress_bar.scale.x = 1.0
			update_visuals()

func on_interact(game) -> void:
	game.handle_incubator_interaction(self)

func plant(seed: String, duration: float) -> void:
	state = State.GROWING
	seed_id = seed
	start_time = Time.get_unix_time_from_system()
	grow_duration = max(duration, 1.0)
	stage_label.text = "Stage 1/%d" % growth_stage_count
	update_visuals()

func force_ready(seed: String, duration: float, started: float) -> void:
	seed_id = seed
	start_time = started
	grow_duration = duration
	state = State.GROWING
	if Time.get_unix_time_from_system() - start_time >= grow_duration:
		state = State.READY
	update_visuals()

func harvest() -> void:
	state = State.EMPTY
	seed_id = ""
	start_time = 0.0
	grow_duration = 0.0
	stage_label.text = "Empty"
	progress_bar.scale.x = 0.0
	update_visuals()

func update_visuals() -> void:
	match state:
		State.EMPTY:
			base_rect.color = Color(0.5, 0.5, 0.65, 1)
			progress_bar.visible = false
		State.GROWING:
			base_rect.color = Color(0.35, 0.7, 0.45, 1)
			progress_bar.visible = true
		State.READY:
			base_rect.color = Color(0.9, 0.8, 0.35, 1)
			progress_bar.visible = true
	if seed_id != "":
		stage_label.modulate = Color(1, 1, 1, 1)
	else:
		stage_label.modulate = Color(1, 1, 1, 0.7)

func get_save_data() -> Dictionary:
	return {
		"id": incubator_id,
		"state": state,
		"seed_id": seed_id,
		"start_time": start_time,
		"grow_duration": grow_duration
	}

func load_save_data(data: Dictionary) -> void:
	if data.is_empty():
		return
	incubator_id = data.get("id", incubator_id)
	state = data.get("state", State.EMPTY)
	seed_id = data.get("seed_id", "")
	start_time = data.get("start_time", 0.0)
	grow_duration = data.get("grow_duration", 0.0)
	if state == State.GROWING and grow_duration > 0:
		var elapsed := Time.get_unix_time_from_system() - start_time
		if elapsed >= grow_duration:
			state = State.READY
	update_visuals()
