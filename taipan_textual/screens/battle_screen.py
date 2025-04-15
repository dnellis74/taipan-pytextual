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


from ..game_state import GameState, BATTLE_NOT_FINISHED, BATTLE_WON, BATTLE_INTERRUPTED, BATTLE_FLED, BATTLE_LOST

# Battle types
GENERIC = 1
LI_YUEN = 2

BattleResult = Literal[0, 1, 2, 3, 4]

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
        self.battle_ships_widget = Static(self.battle_ships, id="battle-ships")
        
        yield Container(
            self.battle_status_widget,
            self.battle_orders_widget,
            self.battle_message_widget,
            self.battle_ships_widget,
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
            self.battle_ships_widget.update(ships)
    
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
    def _update_ships_display(self) -> None:
        """Update the ships display."""
        # TODO: Implement visual ship display
        pass
    
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
                        self._update_ships_display()
            
            # Target a ship
            targeted = random.randint(0, 9)
            while self.ships_on_screen[targeted] == 0:
                targeted = random.randint(0, 9)
            
            # Apply damage
            self.ships_on_screen[targeted] -= random.randint(10, 40)
            
            if self.ships_on_screen[targeted] <= 0:
                self.num_on_screen -= 1
                self.num_ships -= 1
                sk += 1
                self.ships_on_screen[targeted] = 0
            
            # Update display
            self._update_battle_status()
            self._update_ships_display()
            
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
    def _handle_throw_cargo(self) -> None:
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
                await self._update_battle_message("It's worth %s!", self.long_pause);
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