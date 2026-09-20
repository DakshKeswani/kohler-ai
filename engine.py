from catalog import KOHLER_INVENTORY

class BathroomOptimizationEngine:
    def __init__(self, length, width, budget, aesthetic_theme, home_palette, vastu_enabled=True, entrance_dir="South"):
        self.length = float(length)
        self.width = float(width)
        self.total_area = self.length * self.width
        self.budget = float(budget)
        self.aesthetic_theme = aesthetic_theme
        self.home_palette = home_palette
        self.vastu_enabled = vastu_enabled
        self.entrance_dir = entrance_dir
        
        self.palette_finish_map = {
            "Japandi & Warm Earth Tones": ["Vibrant Brushed Bronze", "Vibrant Rose Gold", "Walnut & Matte Gold", "Matte Black PVD"],
            "Modern Obsidian & Industrial Slate": ["Matte Obsidian / Titanium", "Matte Black PVD", "Alpine White", "Vibrant Titanium"],
            "Neo-Classical Parisian Luxury": ["Classic Biscuit", "Vibrant Brass Trim", "Vibrant Brushed Moderne Brass", "Polished Chrome", "French Gold", "Frosted Edge / Ambient Light"]
        }

    def evaluate_bundle(self, bundle):
        total_cost = sum(item["price"] for item in bundle)
        if total_cost > self.budget:
            return None

        # Exclude wall/vanity attachments from floor space math
        combined_footprint = sum(item["w"] * item["d"] for item in bundle if item["category"] not in ["faucet", "mirror", "accessory"])
        if combined_footprint > (self.total_area * 0.40):
            return None

        style_matches = sum(1 for item in bundle if self.aesthetic_theme in item["style"])
        ideal_finishes = self.palette_finish_map.get(self.home_palette, [])
        finish_matches = sum(1 for item in bundle if any(f in item["finish"] for f in ideal_finishes))
        
        style_score = (style_matches / len(bundle)) * 0.50
        finish_score = (finish_matches / len(bundle)) * 0.30
        budget_efficiency = (total_cost / self.budget) * 0.20
        
        return {
            "items": bundle,
            "total_cost": total_cost,
            "remaining_budget": self.budget - total_cost,
            "score": style_score + finish_score + budget_efficiency,
            "footprint_ratio": combined_footprint / self.total_area
        }

    def solve(self):
        categories = ["toilet", "vanity", "shower", "faucet", "mirror"]
        candidates = {cat: [i for i in KOHLER_INVENTORY if i["category"] == cat] for cat in categories}
        
        valid_bundles = []

        # 5-Loop Combinatorial Engine
        for t in candidates.get("toilet", []):
            for v in candidates.get("vanity", []):
                for s in candidates.get("shower", []):
                    for f in candidates.get("faucet", []):
                        for m in candidates.get("mirror", []):
                            bundle = [t, v, s, f, m]
                            result = self.evaluate_bundle(bundle)
                            if result:
                                valid_bundles.append(result)

        if not valid_bundles:
            return []

        # Rank bundles by score
        valid_bundles.sort(key=lambda x: x["score"], reverse=True)
        top_bundles = valid_bundles[:3]
        
        # Route coordinates for the top 3 bundles
        for bundle in top_bundles:
            bundle["items"] = self.route_spatial_coordinates(bundle["items"])
            
        return top_bundles

    def get_door_rect(self):
        """Calculates the physical bounding box of the door swing."""
        door_w = 2.5
        if self.entrance_dir == "South":
            return (self.length / 2, 0, door_w, door_w)
        elif self.entrance_dir == "North":
            return (self.length / 2 - door_w, self.width - door_w, door_w, door_w)
        elif self.entrance_dir == "East":
            return (self.length - door_w, self.width / 2, door_w, door_w)
        else: # West
            return (0, self.width / 2 - door_w, door_w, door_w)

    def check_overlap(self, rect1, rect2):
        """AABB Collision Detection with a 0.2ft physical buffer between items."""
        x1, y1, w1, d1 = rect1
        x2, y2, w2, d2 = rect2
        buffer = 0.2 
        
        if x1 >= (x2 + w2 + buffer) or x2 >= (x1 + w1 + buffer):
            return False
        if y1 >= (y2 + d2 + buffer) or y2 >= (y1 + d1 + buffer):
            return False
        return True

    def find_open_space(self, w, d, placed_rects, door_rect):
        """Scans the room grid to find a valid coordinate that does not overlap anything."""
        for x_int in range(5, int((self.length - w) * 10), 5):
            for y_int in range(5, int((self.width - d) * 10), 5):
                x = x_int / 10.0
                y = y_int / 10.0
                candidate_rect = (x, y, w, d)
                
                if self.check_overlap(candidate_rect, door_rect):
                    continue
                    
                overlap = False
                for placed in placed_rects:
                    if self.check_overlap(candidate_rect, placed):
                        overlap = True
                        break
                        
                if not overlap:
                    return x, y
        return 0.5, 0.5 # Fallback coordinate 

    def route_spatial_coordinates(self, items):
        placed_items = []
        placed_rects = []
        door_rect = self.get_door_rect()
        
        # Split floor items (need collision) from vanity attachments (sit on/above vanity)
        floor_items = [i for i in items if i["category"] not in ["faucet", "mirror"]]
        attachments = [i for i in items if i["category"] in ["faucet", "mirror"]]
        
        sorted_floor = sorted(floor_items, key=lambda i: i["w"] * i["d"], reverse=True)
        vanity_coords = (0.5, 0.5) 
        
        for item in sorted_floor:
            placed_item = item.copy()
            cat = placed_item["category"]
            w, d = placed_item["w"], placed_item["d"]
            
            px, py = 0.5, 0.5
            if self.vastu_enabled:
                if cat == "shower": px, py = self.length - w - 0.5, self.width - d - 0.5
                elif cat == "vanity": px, py = self.length - w - 0.5, 0.5
                elif cat == "toilet": px, py = 0.5, 0.5
            else:
                if cat == "shower": px, py = 0.5, self.width - d - 0.5
                elif cat == "vanity": px, py = 0.5, 0.5
                elif cat == "toilet": px, py = self.length - w - 0.5, 0.5

            ideal_rect = (px, py, w, d)
            
            collision = self.check_overlap(ideal_rect, door_rect)
            for p_rect in placed_rects:
                if self.check_overlap(ideal_rect, p_rect):
                    collision = True
                    break
                    
            if collision:
                px, py = self.find_open_space(w, d, placed_rects, door_rect)

            placed_item["x"] = px
            placed_item["y"] = py
            placed_items.append(placed_item)
            placed_rects.append((px, py, w, d))
            
            # Save vanity coordinates so we can attach the mirror and faucet to it
            if cat == "vanity":
                vanity_coords = (px, py)

        # Snap the mirror and faucet exactly to the vanity's coordinates
        for item in attachments:
            placed_item = item.copy()
            placed_item["x"] = vanity_coords[0]
            # Push the mirror slightly to the "back wall" of the vanity for 2D visual clarity
            placed_item["y"] = vanity_coords[1] + (placed_item["d"] if placed_item["category"] == "mirror" else 0) 
            placed_items.append(placed_item)
            
        return placed_items