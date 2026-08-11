import asyncio
import random
import logging

import keyboard

from rich.color import Color
from rich.text import Text
from rich.live import Live
from rich.style import Style

from core.db.hDatabase import Database
from core.services.services import save_last_matches
from core.stats_api import DBDStats


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("log.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


async def timer(seconds: int):
    with Live(refresh_per_second=10) as live:
        for sec in range(seconds, 0, -1):
            live.update(Text(f"Time to next response: {sec}", style=Style(color=Color.from_rgb(0, 255, 255))))
            await asyncio.sleep(1)

class MainLoop:
    timer_task: asyncio.Task = None
    event_loop: asyncio.AbstractEventLoop = None
    
    @classmethod
    def loop(cls):
        cls.event_loop.call_soon_threadsafe(cls._toggle)

    @classmethod
    def _toggle(cls):
        if cls.timer_task:
            cls.timer_task.cancel()
        
        cls.timer_task = asyncio.create_task(cls.main())
    @classmethod
    async def main(cls):
        time_to_text_res = random.randint(a=(10 * 60), b=(15 * 60))
        while True:
            try:
                last_matches_res = await DBDStats.last_matches()
                await save_last_matches(last_matches_res)       
                await timer(time_to_text_res)
            except Exception as e:
                logger.error(e)

async def main():
    await Database.create_db()
    
    MainLoop.event_loop = asyncio.get_running_loop()
    
    is_running = True    
    def toggle_app_state():
        nonlocal is_running
        is_running = not is_running
    
    keyboard.add_hotkey('alt+r', MainLoop.loop)
    keyboard.add_hotkey('num_0', MainLoop.loop)
    keyboard.add_hotkey('ctrl+end', lambda: toggle_app_state())
        
    print('Press alt+r or numpad0 to force update (send request to dbdstats). Press ctrl+END to exit.')
    
    while is_running:
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())
