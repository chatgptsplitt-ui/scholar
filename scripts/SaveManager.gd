extends Node

const SAVE_PATH := "user://alien_orchard_save.json"

func save_game(data: Dictionary) -> void:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data, "\t"))

func load_game() -> Dictionary:
	if not FileAccess.file_exists(SAVE_PATH):
		return {}
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if not file:
		return {}
	var text := file.get_as_text()
	var result := JSON.parse_string(text)
	if typeof(result) == TYPE_DICTIONARY:
		return result
	return {}
