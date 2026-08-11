
import asyncio
import datetime
import logging
from typing import Any
from aiogram import Bot
from aiogram.types import InputRichMessage

from core.db.h_database import MatchPayloadDAO
from core.json_to_model_parser import ModelItem, StatsParser
from core.services.config import CHAT_ID, TELEGRAM_BOT_TOKEN
from core.stats_api import DBDStats

bot = Bot(token=TELEGRAM_BOT_TOKEN)
id = CHAT_ID

logger = logging.getLogger(__name__)

async def get_match(matchStartTime: int):
    match = await MatchPayloadDAO.get(matchStartTime=matchStartTime)
    return StatsParser.parse_match(match.payload)

async def save_last_matches(last_matches: list[dict[str, Any]]):
    send_queue = []
    last_matches.reverse()
    for match in last_matches:
        if await MatchPayloadDAO.add(match):
            
            obj_match = StatsParser.parse_match(match)
            logger.info(f"Match {obj_match.matchStat.matchStartTime} {obj_match.playerStat.characterName.name} saved.")

            send_queue.append(obj_match)
    if last_matches:
        logger.info("All Available matches saved.")
            
    for obj in send_queue:
        await send_match_info_into_tg(obj)
        await asyncio.sleep(1)

async def send_match_info_into_tg(match: ModelItem):
    
    from core.services.telegram_utils import CustomEmoji
    from core.services.dataclasses import DBDIcons, DBDDicts
    
    text = f'''
        <h5>{CustomEmoji(DBDIcons.survivors[match.playerStat.characterName.id] if match.playerStat.playerRole == "VE_Camper" else DBDIcons.killers[match.playerStat.characterName.id])} {match.playerStat.characterName.name}, {CustomEmoji(5431377838219494379)}{match.playerStat.playerStatus.name or match.playerStat.playerStatus.id if match.playerStat.playerRole == "VE_Camper" else match.playerStat.killerMatchStatus}</h5>
        <b>Map: {match.matchStat.map.name}</b>
        <img src="{await DBDStats.get_asset(match.matchStat.map.image.path, "dbdstat")}" alt="{match.matchStat.map.name}"/>
        <blockquote>Общая сводка:<br>
            <b>{CustomEmoji(5841276284155467413)} Айди матча:</b> <code>{match.matchStat.matchStartTime}</code>
            <br>
            <b>{CustomEmoji(5251690622896593207)} Старт: <code>{datetime.datetime.fromtimestamp(match.matchStat.matchStartTime).strftime("%d.%m.%Y %H:%M:%S")}</code></b>
            <br>
            <b>{CustomEmoji(5370569566688666025)} Конец: <code>{(datetime.datetime.fromtimestamp(match.matchStat.matchStartTime) + datetime.timedelta(seconds=match.matchStat.matchDuration)).strftime("%d.%m.%Y %H:%M:%S")}</code></b>
            <br>
            <b>{CustomEmoji(5372853441318105454)} Длительность: <code>{datetime.datetime.fromtimestamp(match.matchStat.matchDuration) - datetime.datetime.fromtimestamp(0)}</code></b>
            <br>
            <b>{CustomEmoji(5222046110079553744)} BP: <code>{match.playerStat.bloodpointsEarned}</code></b>        
        </blockquote>
        <blockquote>    
            <b>{f"Brutality: <code>{match.playerStat.postGameStat.DBD_SlasherScoreCat_Brutality or 0}</code>" if match.playerStat.playerRole == "VE_Slasher" else f"Altruism: <code>{match.playerStat.postGameStat.DBD_CamperScoreCat_Altruism or 0}</code>"}</b><br>
            <b>{f"Deviousness: <code>{match.playerStat.postGameStat.DBD_SlasherScoreCat_Deviousness or 0}</code>" if match.playerStat.playerRole == "VE_Slasher" else f"Boldness: <code>{match.playerStat.postGameStat.DBD_CamperScoreCat_Boldness or 0}</code>"}</b><br>
            <b>{f"Hunter: <code>{match.playerStat.postGameStat.DBD_SlasherScoreCat_Hunter or 0}</code>" if match.playerStat.playerRole == "VE_Slasher" else f"Objectives: <code>{match.playerStat.postGameStat.DBD_CamperScoreCat_Objectives or 0}</code>"}</b><br>
            <b>{f"Sacrifice: <code>{match.playerStat.postGameStat.DBD_SlasherScoreCat_Sacrifice or 0}</code>" if match.playerStat.playerRole == "VE_Slasher" else f"Survival: <code>{match.playerStat.postGameStat.DBD_CamperScoreCat_Survival or 0}</code>"}</b><br>           
        </blockquote>
        <blockquote expandable>
            <b>Perks:</b><br>
            {"<br>".join([f"<a href=\"https://deadbydaylight.wiki.gg/wiki/{perk.name.replace(" ", "_").replace("’", "%27").replace("‘", "%27")}\">{perk.name}</a>" for perk in (match.playerStat.characterLoadout.perks or []) if perk != "None"])}
        </blockquote>
        <details open>
            <summary>Opponents</summary>
            {"".join(
                [f"""
                <details>
                    <blockquote><h5>General</h5><br>
                        <b>Platform: <code>{opp.platform and opp.platform.capitalize() or "[UNKNOWN]"}</code></b><br>
                        <b>Prestige: <code>{opp.prestigeLevel or "[UNKNOWN]"}</code> | Level: <code>{opp.characterLevel}</code></b><br>
                        <b>{CustomEmoji(5256224356014503374)} Time in match: <code>{datetime.datetime.fromtimestamp(abs(opp.playerTimeInMatch)) - datetime.datetime.fromtimestamp(0)}</code></b><br>
                        <b>{CustomEmoji(5222046110079553744)} BP: <code>{opp.bloodpointsEarned or 0}</code></b>
                    </blockquote>
                    <blockquote><h5>Post Game Stats</h5><br>
                        <b>{f"Brutality: <code>{opp.postGameStat.DBD_SlasherScoreCat_Brutality or 0}</code>" if opp.playerRole == "VE_Slasher" else f"Altruism: <code>{opp.postGameStat.DBD_CamperScoreCat_Altruism or 0}</code>"}</b><br>
                        <b>{f"Deviousness: <code>{opp.postGameStat.DBD_SlasherScoreCat_Deviousness or 0}</code>" if opp.playerRole == "VE_Slasher" else f"Boldness: <code>{opp.postGameStat.DBD_CamperScoreCat_Boldness or 0}</code>"}</b><br>
                        <b>{f"Hunter: <code>{opp.postGameStat.DBD_SlasherScoreCat_Hunter or 0}</code>" if opp.playerRole == "VE_Slasher" else f"Objectives: <code>{opp.postGameStat.DBD_CamperScoreCat_Objectives or 0}</code>"}</b><br>
                        <b>{f"Sacrifice: <code>{opp.postGameStat.DBD_SlasherScoreCat_Sacrifice or 0}</code>" if opp.playerRole == "VE_Slasher" else f"Survival: <code>{opp.postGameStat.DBD_CamperScoreCat_Survival or 0}</code>"}</b><br>           
                    </blockquote>
                    <summary>{opp.characterName.name} - {DBDDicts.PlayerStatus.get(opp.playerStatus and opp.playerStatus.id) or opp.killerMatchStatus}</summary>
                    <blockquote><h5>Perks</h5><br>
                        {"<br>".join([f"<a href=\"https://deadbydaylight.wiki.gg/wiki/{perk.name.replace(" ", "_")}\">{perk.name}</a>" for perk in opp.characterLoadout.perks or []])}
                    </blockquote>
                    <blockquote><h5>Power</h5><br>                   
                        <a href=\"https://deadbydaylight.wiki.gg/wiki/{opp.characterLoadout.power and opp.characterLoadout.power.name.replace(" ", "_") or "[NO URL]"}\">{opp.characterLoadout.power and opp.characterLoadout.power.name or "[NO POWER]"}</a><br>
                        {"<br>".join([f"+ <a href=\"https://deadbydaylight.wiki.gg/wiki/{addon.name.replace(" ", "_").replace("’", "%27").replace("‘", "%27")}\">{addon.name}</a>" for addon in opp.characterLoadout.addOns or []])}
                    </blockquote>
                    <blockquote><h5>Offering</h5><br>
                    <a href=\"https://deadbydaylight.wiki.gg/wiki/{opp.characterLoadout.offering and opp.characterLoadout.offering.name.replace(" ", "_") or "[NO URL]"}\">{opp.characterLoadout.offering and opp.characterLoadout.offering.name or "[NO OFFERING]"}</a>
                </details>
                """ for opp in match.opponentStat or []]
                )
            }         
        </details>
        '''
    try:
        if await bot.send_rich_message(chat_id=id, rich_message=InputRichMessage(html=text)):
            return True
    finally:
        await bot.session.close()
    return False