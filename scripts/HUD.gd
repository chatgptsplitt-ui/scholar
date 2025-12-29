extends Control

var game_ref: Node = null

@onready var credits_label: Label = $MarginContainer/VBoxContainer/TopBar/CreditsLabel
@onready var seed_label: Label = $MarginContainer/VBoxContainer/TopBar/SelectedSeedLabel
@onready var prompt_label: Label = $InteractionPrompt
@onready var incubator_panel: Panel = $IncubatorPanel
@onready var incubator_name: Label = $IncubatorPanel/VBoxContainer/SeedName
@onready var incubator_stage: Label = $IncubatorPanel/VBoxContainer/Stage
@onready var incubator_time: Label = $IncubatorPanel/VBoxContainer/TimeRemaining
@onready var shop_panel: Panel = $ShopPanel
@onready var shop_list: VBoxContainer = $ShopPanel/MarginContainer/VBoxContainer/SeedList
@onready var quickbar: HBoxContainer = $MarginContainer/VBoxContainer/Quickbar
@onready var message_label: Label = $PopupMessage

func set_game(game) -> void:
	game_ref = game

func update_top(credits: int, selected_seed: Dictionary) -> void:
	credits_label.text = "Credits: %d" % credits
	if selected_seed.is_empty():
		seed_label.text = "Selected Seed: None"
	else:
		seed_label.text = "Selected Seed: %s" % selected_seed.get("name", "Seed")

func update_quickbar(seeds: Array, selected_index: int, inventory: Dictionary) -> void:
	for i in range(quickbar.get_child_count()):
		var btn := quickbar.get_child(i) as Button
		if i < seeds.size():
			var seed := seeds[i]
			var count := inventory.get(seed["id"], 0)
			btn.text = "%d: %s (%d)" % [i + 1, seed["name"], count]
			btn.disabled = false
		else:
			btn.text = "%d: Empty" % (i + 1)
			btn.disabled = true
		btn.button_pressed = (i == selected_index)

func show_prompt(text: String) -> void:
	prompt_label.text = text
	prompt_label.visible = true

func hide_prompt() -> void:
	prompt_label.visible = false

func show_incubator(seed_name: String, stage_text: String, time_remaining: String) -> void:
	incubator_panel.visible = true
	incubator_name.text = seed_name
	incubator_stage.text = stage_text
	incubator_time.text = time_remaining

func hide_incubator() -> void:
	incubator_panel.visible = false

func toggle_shop(visible: bool, seed_catalog: Array = [], inventory: Dictionary = {}, credits: int = 0) -> void:
	shop_panel.visible = visible
	if not visible:
		return
	for child in shop_list.get_children():
		child.queue_free()
	for seed in seed_catalog:
		var row := HBoxContainer.new()
		var label := Label.new()
		label.text = "%s | Grow %ss | Buy %d | Sell %d | %s" % [seed["name"], seed["growTimeSeconds"], seed["buyCost"], seed["sellValue"], seed["rarity"]]
		label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var button := Button.new()
		button.text = "Buy"
		var id := seed["id"]
		button.pressed.connect(func():
			if game_ref:
				game_ref.buy_seed(id)
		)
		var select_button := Button.new()
		select_button.text = "Select"
		select_button.pressed.connect(func():
			if game_ref:
				game_ref.select_seed(id)
		)
		row.add_child(label)
		row.add_child(button)
		row.add_child(select_button)
		shop_list.add_child(row)
	var close := Button.new()
	close.text = "Close"
	close.pressed.connect(func():
		if game_ref:
			game_ref.close_shop()
	)
	shop_list.add_child(close)

func set_message(text: String) -> void:
	message_label.text = text
	message_label.modulate = Color(1,1,1,1)
	message_label.visible = true
	message_label.create_tween().tween_property(message_label, "modulate:a", 0.0, 1.0).set_trans(Tween.TRANS_SINE)
