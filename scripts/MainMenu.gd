extends Control

func _ready() -> void:
	$CenterContainer/VBoxContainer/NewGameButton.pressed.connect(_on_new_game)
	$CenterContainer/VBoxContainer/ContinueButton.pressed.connect(_on_continue)
	$CenterContainer/VBoxContainer/QuitButton.pressed.connect(_on_quit)

func _on_new_game() -> void:
	SaveManager.save_game({})
	get_tree().change_scene_to_file("res://scenes/Game.tscn")

func _on_continue() -> void:
	get_tree().change_scene_to_file("res://scenes/Game.tscn")

func _on_quit() -> void:
	get_tree().quit()
