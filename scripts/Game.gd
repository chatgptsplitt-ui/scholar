extends Node2D

@onready var player: CharacterBody2D = $Player
@onready var hud: Control = $CanvasLayer/HUD
@onready var rooms_node: Node = $Rooms

var seed_catalog: Array = []
var inventory := {}
var credits: int = 100
var unlocked_rooms := {"Room_01": true, "Room_02": false, "Room_03": false}
var room_prices := {"Room_02": 400, "Room_03": 900}
var selected_seed_index: int = 0
var shop_open: bool = false
var mutation_chance := 0.15
var room_bounds := {
	"Room_01": Rect2(Vector2(80, 120), Vector2(560, 260)),
	"Room_02": Rect2(Vector2(100, 120), Vector2(620, 260)),
	"Room_03": Rect2(Vector2(120, 140), Vector2(660, 260))
}

func _ready() -> void:
	hud.set_game(self)
	load_seed_catalog()
	load_game()
	setup_rooms()
	hud.update_top(credits, get_selected_seed())
	hud.update_quickbar(seed_catalog, selected_seed_index, inventory)

func load_seed_catalog() -> void:
	var file := FileAccess.open("res://data/seeds.json", FileAccess.READ)
	if file:
		var text := file.get_as_text()
		var result := JSON.parse_string(text)
		if typeof(result) == TYPE_ARRAY:
			seed_catalog = result

func setup_rooms() -> void:
	for room in rooms_node.get_children():
		if room.has_method("configure"):
			room.configure(self)
		if room.has_node("Door"):
			var door := room.get_node("Door")
			var id := door.room_id
			door.locked = not unlocked_rooms.get(id, id == "Room_01")
			door.update_visuals()

func handle_incubator_interaction(incubator: Node) -> void:
	if shop_open:
		return
	var state = incubator.state
	match state:
		incubator.State.EMPTY:
			var seed := get_selected_seed()
			if seed.is_empty():
				hud.set_message("No seed selected.")
				return
			var count := inventory.get(seed["id"], 0)
			if count <= 0:
				hud.set_message("You have no %s." % seed["name"])
				return
			inventory[seed["id"]] = count - 1
			incubator.plant(seed["id"], seed["growTimeSeconds"])
			hud.set_message("Planted %s." % seed["name"])
		incubator.State.GROWING:
			var elapsed := Time.get_unix_time_from_system() - incubator.start_time
			var remaining := max(incubator.grow_duration - elapsed, 0)
			var seed_name := get_seed_name(incubator.seed_id)
			hud.show_incubator("Incubator: %s" % seed_name, "Growing", "%.1fs remaining" % remaining)
			return
		incubator.State.READY:
			var payout := harvest_seed(incubator.seed_id)
			incubator.harvest()
			credits += payout
			hud.set_message("Harvested for %d credits." % payout)
	hud.update_top(credits, get_selected_seed())
	hud.update_quickbar(seed_catalog, selected_seed_index, inventory)
	hud.hide_incubator()

func harvest_seed(seed_id: String) -> int:
	var seed := seed_catalog.filter(func(s): return s["id"] == seed_id)
	if seed.is_empty():
		return 0
	var entry := seed[0]
	var sell := entry.get("sellValue", 0)
	if entry.get("trait", "").find("Bioluminescent") != -1:
		sell = int(sell * 1.1)
	if randf() < mutation_chance:
		sell = int(sell * 1.4)
		hud.set_message("Mutation! Bonus payout.")
	return sell

func handle_door_interaction(door: Node) -> void:
	var id := door.room_id
	if unlocked_rooms.get(id, false):
		switch_room(door.target_room)
		return
	var cost := door.price
	if credits >= cost:
		credits -= cost
		unlocked_rooms[id] = true
		door.locked = false
		door.update_visuals()
		hud.set_message("Unlocked %s." % id)
	else:
		hud.set_message("Need %d credits." % cost)
	hud.update_top(credits, get_selected_seed())

func switch_room(room_name: String) -> void:
	for room in rooms_node.get_children():
		room.visible = room.name == room_name
	player.global_position = rooms_node.get_node(room_name).get_spawn_position()
	hud.hide_incubator()

func get_selected_seed() -> Dictionary:
	if seed_catalog.is_empty():
		return {}
	return seed_catalog[selected_seed_index]

func get_seed_name(id: String) -> String:
	for seed in seed_catalog:
		if seed["id"] == id:
			return seed["name"]
	return "Unknown"

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		save_game()
	for i in range(5):
		if event.is_action_pressed("quick_%d" % (i + 1)):
			if i < seed_catalog.size():
				selected_seed_index = i
				hud.update_quickbar(seed_catalog, selected_seed_index, inventory)
				hud.update_top(credits, get_selected_seed())
	if event.is_action_pressed("interact") and shop_open:
		close_shop()

func show_interaction_prompt(body: Node) -> void:
	if body is Area2D:
		if body.is_in_group("incubator"):
			hud.show_prompt("E: interact")
		elif body is Area2D:
			hud.show_prompt("E: interact")

func hide_interaction_prompt() -> void:
	hud.hide_prompt()
	hud.hide_incubator()

func open_shop() -> void:
	shop_open = true
	hud.toggle_shop(true, seed_catalog, inventory, credits)

func buy_seed(seed_id: String) -> void:
	var seed := seed_catalog.filter(func(s): return s["id"] == seed_id)
	if seed.is_empty():
		return
	var entry := seed[0]
	var cost := entry.get("buyCost", 0)
	if credits < cost:
		hud.set_message("Not enough credits.")
		return
	credits -= cost
	inventory[seed_id] = inventory.get(seed_id, 0) + 1
	hud.update_top(credits, get_selected_seed())
	hud.update_quickbar(seed_catalog, selected_seed_index, inventory)

func close_shop() -> void:
	shop_open = false
	hud.toggle_shop(false)

func save_game() -> void:
	var data := {
		"credits": credits,
		"inventory": inventory,
		"unlocked_rooms": unlocked_rooms,
		"incubators": []
	}
	for room in rooms_node.get_children():
		for inc in room.get_incubators():
			data["incubators"].append(inc.get_save_data())
	SaveManager.save_game(data)
	hud.set_message("Game saved.")

func load_game() -> void:
	var data := SaveManager.load_game()
	if data.is_empty():
		initialize_default()
		return
	credits = data.get("credits", credits)
	inventory = data.get("inventory", {})
	unlocked_rooms = data.get("unlocked_rooms", unlocked_rooms)
	var incubator_data: Array = data.get("incubators", [])
	for room in rooms_node.get_children():
		for inc in room.get_incubators():
			for saved in incubator_data:
				if saved.get("id", "") == inc.incubator_id:
					inc.load_save_data(saved)
	hud.set_message("Loaded save.")

func initialize_default() -> void:
	credits = 100
	inventory = {"glow_puff": 3, "spore_bulb": 1}
	unlocked_rooms = {"Room_01": true, "Room_02": false, "Room_03": false}

func purchase_room(room_id: String) -> void:
	var price := room_prices.get(room_id, 0)
	if unlocked_rooms.get(room_id, false):
		return
	if credits >= price:
		credits -= price
		unlocked_rooms[room_id] = true
		hud.set_message("Unlocked %s" % room_id)
		hud.update_top(credits, get_selected_seed())

func _physics_process(delta: float) -> void:
	var current_room := ""
	for room in rooms_node.get_children():
		if room.visible:
			current_room = room.name
	var bounds: Rect2 = room_bounds.get(current_room, Rect2(Vector2.ZERO, Vector2(800, 480)))
	player.position.x = clamp(player.position.x, bounds.position.x, bounds.position.x + bounds.size.x)
	player.position.y = clamp(player.position.y, bounds.position.y, bounds.position.y + bounds.size.y)

func select_seed(seed_id: String) -> void:
	for i in range(seed_catalog.size()):
		if seed_catalog[i].get("id", "") == seed_id:
			selected_seed_index = i
			hud.update_top(credits, get_selected_seed())
			hud.update_quickbar(seed_catalog, selected_seed_index, inventory)
			return
