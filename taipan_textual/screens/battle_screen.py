"""
Battle screen for sea battles in Taipan.
"""

from typing import Union, Optional, cast, Literal
from taipan_textual.screens.complete_travel_screen import CompleteTravelScreen
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Input
from textual.containers import Container
from textual import events, work
import random
import asyncio
from rich.panel import Panel
from rich.text import Text
from textual.reactive import reactive
from textual.worker import Worker
from textual.geometry import Region
from rich.style import Style


from ..game_state import GameState, BATTLE_NOT_FINISHED, BATTLE_WON, BATTLE_INTERRUPTED, BATTLE_FLED, BATTLE_LOST

# Battle types
GENERIC = 1
LI_YUEN = 2

BattleResult = Literal[0, 1, 2, 3, 4]

class ShipDisplay(Static):
    """Widget for displaying ships in battle."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ships = [0] * 10  # Health of ships in each position
        self.explosions = [False] * 10  # Whether each position is exploding
        self.sinking = [False] * 10  # Whether each position is sinking
        self.sink_frames = [0] * 10  # Current frame of sinking animation
        self._lines = []  # Store the current display lines
        self.num_ships = 0  # Number of ships currently in battle
        self.num_on_screen = 0  # Number of ships currently displayed
        self.enemy_health = 0  # Enemy health for backfilling ships
        
    def initialize_ships(self, num_ships: int, enemy_health: int) -> None:
        """Initialize ships for battle, matching the C code logic."""
        self.num_ships = num_ships
        self.num_on_screen = 0
        self.ships = [0] * 10
        self.enemy_health = enemy_health
        
        # Fill the first 5 positions with ships
        for i in range(min(5, num_ships)):
            self.ships[i] = int((enemy_health * random.random()) + 20)
            self.num_on_screen += 1
            
        # If more than 5 ships, fill the second row
        if num_ships > 5:
            for i in range(5, min(10, num_ships)):
                self.ships[i] = int((enemy_health * random.random()) + 20)
                self.num_on_screen += 1
                
        self.refresh()
        
    def backfill_ships(self) -> None:
        """Backfill empty positions with new ships if there are still ships remaining."""
        if self.num_ships > self.num_on_screen:
            # Find empty positions and fill them
            for i in range(10):
                if self.ships[i] == 0 and self.num_ships > self.num_on_screen:
                    self.ships[i] = int((self.enemy_health * random.random()) + 20)
                    self.num_on_screen += 1
            self.refresh()
        
    def draw_ship(self, x: int, y: int) -> None:
        """Draw a ship at the given position."""
        self._write_at(x, y, "-|-_|_  ")
        self._write_at(x, y + 1, "-|-_|_  ")
        self._write_at(x, y + 2, "_|__|__/")
        self._write_at(x, y + 3, "\\_____/ ")
        
    def draw_explosion(self, x: int, y: int) -> None:
        """Draw an explosion at the given position."""
        self._write_at(x, y, "********")
        self._write_at(x, y + 1, "********")
        self._write_at(x, y + 2, "********")
        self._write_at(x, y + 3, "********")
        
    def clear_position(self, x: int, y: int) -> None:
        """Clear the given position."""
        self._write_at(x, y, "        ")
        self._write_at(x, y + 1, "        ")
        self._write_at(x, y + 2, "        ")
        self._write_at(x, y + 3, "        ")
        
    def _write_at(self, x: int, y: int, text: str) -> None:
        """Write text at the given position."""
        # Ensure we have enough lines
        while len(self._lines) <= y + 1:
            self._lines.append("")
            
        # Ensure the line is long enough
        while len(self._lines[y]) < x + len(text):
            self._lines[y] += " "
            
        # Insert the text
        self._lines[y] = self._lines[y][:x] + text + self._lines[y][x + len(text):]
        
    def render(self) -> str:
        """Render the ship display."""
        # Clear the display
        self._lines = []
        
        # Draw ships in their current positions
        for i in range(10):
            if self.ships[i] > 0:
                x = 10 + (i % 5) * 10
                y = 6 if i < 5 else 12
                
                if self.explosions[i]:
                    self.draw_explosion(x, y)
                elif self.sinking[i]:
                    # Draw sinking animation frame
                    if self.sink_frames[i] == 0:
                        self.clear_position(x, y)
                        self.draw_ship(x, y + 1)
                    elif self.sink_frames[i] == 1:
                        self.clear_position(x, y + 1)
                        self.draw_ship(x, y + 2)
                    elif self.sink_frames[i] == 2:
                        self.clear_position(x, y + 2)
                        self.draw_ship(x, y + 3)
                    else:
                        self.clear_position(x, y + 3)
                else:
                    self.draw_ship(x, y)
                    
        return "\n".join(self._lines)
        
    async def animate_sinking(self, index: int) -> None:
        """Animate a ship sinking."""
        self.sinking[index] = True
        self.sink_frames[index] = 0
        
        for frame in range(4):
            self.sink_frames[index] = frame
            self.refresh()
            await asyncio.sleep(0.5)
            
        self.sinking[index] = False
        self.sink_frames[index] = 0
        self.ships[index] = 0
        self.num_on_screen -= 1
        self.num_ships -= 1
        
        # Backfill if there are still ships remaining
        self.backfill_ships()
        
        self.refresh()
        
    async def animate_explosion(self, index: int) -> None:
        """Animate an explosion."""
        self.explosions[index] = True
        self.refresh()
        await asyncio.sleep(0.1)
        self.explosions[index] = False
        self.refresh()

class BattleScreen(Screen):
    """Screen for handling sea battles."""
    
    # Reactive attributes for battle state
    battle_status = reactive("")
    battle_message = reactive("")
    battle_orders = reactive("")
    battle_ships = reactive("")
    
    CSS = """
    #battle-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    #battle-status {
        width: 100%;
        height: auto;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }
    
    #battle-message {
        width: 100%;
        height: auto;
        padding: 1;
        background: $panel;
        border: solid $primary;
        margin-top: 1;
    }
    
    #battle-ships {
        width: 100%;
        height: auto;
        padding: 1;
        background: $panel;
        border: solid $primary;
        margin-top: 1;
    }
    
    #battle-orders {
        width: 100%;
        height: auto;
        padding: 1;
        background: $panel;
        border: solid $primary;
        margin-top: 1;
    }
    """
    
    def __init__(
        self, 
        game_state: GameState, 
        battle_type: int = GENERIC,
        num_ships: int = 1,
        name: Union[str, None] = None, 
        id: Union[str, None] = None, 
        classes: Union[str, None] = None
    ) -> None:
        super().__init__(name, id, classes)
        self.game_state = game_state
        self.battle_type = battle_type
        self.num_ships = num_ships
        self.original_ships = num_ships
        self.orders = 0
        self.num_on_screen = 0
        self.ships_on_screen = [0] * 10
        self.ok = 0
        self.ik = 1
        self.time = ((self.game_state.year - 1860) * 12) + self.game_state.month
        
        # Calculate booty
        self.booty = (self.time // 4 * 1000 * num_ships) + random.randint(0, 999) + 250
        
        self.long_pause = 1.5
        self.short_pause = 0.5
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        self.battle_status_widget = Static(self.battle_status, id="battle-status")
        self.battle_orders_widget = Static(self.battle_orders, id="battle-orders")
        self.battle_message_widget = Static(self.battle_message, id="battle-message")
        self.ship_display = ShipDisplay(id="battle-ships")
        
        yield Container(
            self.battle_status_widget,
            self.battle_orders_widget,
            self.battle_message_widget,
            self.ship_display,
            id="battle-container"
        )
    
    def on_mount(self) -> None:
        """Set up the screen when it is mounted."""
        self.battle_status = f"{self.num_ships} hostile ships approaching, Taipan!"
        self.battle_orders = "Taipan, what shall we do??    (f=Fight, r=Run, t=Throw cargo)"
        self._update_battle_status()
        
        # Explicitly update the widgets to reflect the initial values
        self.battle_status_widget.update(self.battle_status)
        self.battle_orders_widget.update(self.battle_orders)
    
    def watch_battle_status(self, status: str) -> None:
        """Called when battle_status changes."""
        if self.is_mounted:
            self.battle_status_widget.update(status)
    
    def watch_battle_message(self, message: str) -> None:
        """Called when battle_message changes."""
        if self.is_mounted:
            self.battle_message_widget.update(message)
    
    def watch_battle_orders(self, orders: str) -> None:
        """Called when battle_orders changes."""
        if self.is_mounted:
            self.battle_orders_widget.update(orders)
    
    def watch_battle_ships(self, ships: str) -> None:
        """Called when battle_ships changes."""
        if self.is_mounted:
            self.ship_display.ships = [int(x) if x else 0 for x in ships.split(',')]
            self.ship_display.refresh()
    
    def _update_battle_status(self) -> None:
        """Update the battle status display."""
        status = 100 - ((self.game_state.damage / self.game_state.capacity) * 100)
        status_text = "Perfect" if status >= 100 else \
                     "Prime" if status >= 80 else \
                     "Good" if status >= 60 else \
                     "Fair" if status >= 40 else \
                     "Poor" if status >= 20 else "Critical"
        
        self.battle_status = (
            f"Current seaworthiness: {status_text} ({int(status)}%)\n"
            f"Ships remaining: {self.num_ships}\n"
            f"Guns: {self.game_state.guns}\n"
            f"Hold: {self.game_state.hold}/{self.game_state.capacity}"
        )
    
    async def _update_battle_message(self, message: str, delay: float) -> None:
        """Update the battle message display."""
        self.battle_message = message
        await asyncio.sleep(delay)
    
    def _update_battle_orders(self, message: str) -> None:
        """Update the battle orders display."""
        self.battle_orders = message
    
    @work
    async def _handle_fight(self) -> None:
        """Handle fight orders."""
        if self.game_state.guns == 0:
            await self._update_battle_message("We have no guns, Taipan!!", self.short_pause)
            return
        
        await self._update_battle_message("Aye, we'll fight 'em, Taipan.", self.short_pause)
        
        await self._update_battle_message("We're firing on 'em, Taipan!", self.short_pause)
        
        sk = 0  # Ships sunk
        for i in range(1, self.game_state.guns + 1):
            if self.num_ships == 0:
                break
            
            # Fill empty ship slots with new ships
            if self.num_ships > self.num_on_screen:
                for j in range(10):
                    if self.ships_on_screen[j] == 0:
                        self.ships_on_screen[j] = int((self.game_state.enemy_health * random.random()) + 20)
                        self.num_on_screen += 1
                        self.ship_display.ships[j] = self.ships_on_screen[j]
                        self.ship_display.refresh()
            
            # Target a ship
            targeted = random.randint(0, 9)
            while self.ships_on_screen[targeted] == 0:
                targeted = random.randint(0, 9)
            
            # Show explosion
            await self.ship_display.animate_explosion(targeted)
            
            # Apply damage
            self.ships_on_screen[targeted] -= random.randint(10, 40)
            
            if self.ships_on_screen[targeted] <= 0:
                self.num_on_screen -= 1
                self.num_ships -= 1
                sk += 1
                self.ships_on_screen[targeted] = 0
                await self.ship_display.animate_sinking(targeted)
            
            # Update display
            self._update_battle_status()
            self.ship_display.refresh()
            
            if i < self.game_state.guns:
                await self._update_battle_message(f"({self.game_state.guns - i} shots remaining.)", 0.5)
        
        if sk > 0:
            await self._update_battle_message(f"Sunk {sk} of the buggers, Taipan!", self.short_pause)
        else:
            await self._update_battle_message("Hit 'em, but didn't sink 'em, Taipan!", self.short_pause)
        
        # Check if some ships run away
        if (random.randint(1, self.original_ships) > (self.num_ships * 0.6 / self.battle_type) and 
            self.num_ships > 2):
            divisor = self.num_ships // 3 // self.battle_type
            if divisor == 0:
                divisor = 1
            ran = random.randint(1, divisor)
            self.num_ships -= ran
            
            self._update_battle_status()
            await self._update_battle_message(f"{ran} ran away, Taipan!", self.short_pause)
            
        await self.after_action()
    
    @work
    async def _handle_run(self) -> None:
        """Handle run orders."""
        await self._update_battle_message("Aye, we'll run, Taipan.", self.short_pause)
        
        self.ok += self.ik
        self.ik += 1
        
        if random.randint(1, self.ok) > random.randint(1, self.num_ships):
            await self._update_battle_message("We got away from 'em, Taipan!", self.short_pause)
            self.num_ships = 0
        else:
            await self._update_battle_message("Couldn't lose 'em.", self.short_pause)
            
            if self.num_ships > 2 and random.randint(1, 5) == 1:
                lost = random.randint(1, self.num_ships // 2)
                self.num_ships -= lost
                
                self._update_battle_status()
                await self._update_battle_message(f"But we escaped from {lost} of 'em!", self.short_pause)
                
                # Get new orders
                self.orders = 0
                self._update_battle_orders("Taipan, what shall we do??    (f=Fight, r=Run, t=Throw cargo)")
    
    @work
    async def _handle_throw_cargo(self) -> None:
        """Handle throw cargo orders."""
        # TODO: Implement cargo throwing
        self._update_battle_orders("What shall I throw overboard, Taipan? (o=Opium, s=Silk, a=Arms, g=General, *=All)")
        # TODO: Handle cargo selection and amount
        pass
    
    async def _handle_enemy_attack(self) -> BattleResult:
        """Handle enemy attack."""
        await self._update_battle_message("They're firing on us, Taipan!", self.short_pause)
        # TODO: Implement visual attack effect
        await self._update_battle_message("We've been hit, Taipan!!", self.short_pause)
        
        # Calculate damage
        i = min(15, self.num_ships)
        if (self.game_state.guns > 0 and 
            (random.randint(1, 100) < ((self.game_state.damage / self.game_state.capacity) * 100) or
             ((self.game_state.damage / self.game_state.capacity) * 100) > 80)):
            i = 1
            self.game_state.guns -= 1
            self.game_state.hold += 10
            await self._update_battle_message("The buggers hit a gun, Taipan!!", self.short_pause)
        
        damage = int((self.game_state.enemy_damage * i * self.battle_type * random.random()) + (i / 2))
        self.game_state.damage += damage
        
        if self.battle_type == GENERIC and random.randint(1, 20) == 1:
            self.app.switch_screen(CompleteTravelScreen(self.game_state))
            return BATTLE_INTERRUPTED
        
        self._update_battle_status()
        return BATTLE_NOT_FINISHED
    
    async def after_action(self) -> None:
        # Handle enemy attack after player's action
        if self.num_ships > 0:
            result = await self._handle_enemy_attack()
            if result != BATTLE_NOT_FINISHED:
                if result == BATTLE_LOST:
                    self.notify("Your ship has been lost!", severity="error")
                self.app.switch_screen(CompleteTravelScreen(self.game_state))
                return
        
        # Check if battle is won
        if self.num_ships == 0:
            if self.orders == 1:
                await self._update_battle_message("We got 'em all, Taipan!", self.short_pause)
                await self._update_battle_message("We captured some booty.\n",self.short_pause);
                await self._update_battle_message(f"It's worth {self.booty}!", self.long_pause);
                self.game_state.cash += self.booty
                self.app.switch_screen(CompleteTravelScreen(self.game_state))
                return
            else:
                self.app.switch_screen(CompleteTravelScreen(self.game_state))
                return
        
        # Check if ship is lost
        status = 100 - ((self.game_state.damage / self.game_state.capacity) * 100)
        if status <= 0:
            self.notify("Your ship has been lost!", severity="error")
            self.app.switch_screen(CompleteTravelScreen(self.game_state))
            return
        
        # Reset orders for next turn
        self.orders = 0
        self._update_battle_orders("Taipan, what shall we do??    (f=Fight, r=Run, t=Throw cargo)") 
    
    async def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if self.orders == 0:
            if event.key.lower() == 'f':
                self.orders = 1
                self._update_battle_orders("Fighting!")
                self._handle_fight()
            elif event.key.lower() == 'r':
                self.orders = 2
                self._update_battle_orders("Fleeing!")
                self._handle_run()
            elif event.key.lower() == 't':
                self.orders = 3
                self._update_battle_orders("Throwing cargo!")
                self._handle_throw_cargo()
            else:
                self._update_battle_orders("Taipan, what shall we do??    (f=Fight, r=Run, t=Throw cargo)")
                return