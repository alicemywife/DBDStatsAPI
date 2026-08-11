
import asyncio
import datetime
import logging
from typing import Any
from aiogram import Bot
from aiogram.types import InputRichMessage

from core.db.hDatabase import MatchPayloadDAO
from core.parser import ModelItem, StatsParser
from core.stats_api import DBDStats
from core.schemas.last_matches_schema import CharacterLoadout, Perk

bot = Bot(token="8374418085:AAHWaowz8jIEtCyrr3O0laBuRpwU4ANn824")
id = 8529684742

logger = logging.getLogger(__name__)

async def get_match(matchStartTime: int):
    match = await MatchPayloadDAO.get(matchStartTime=matchStartTime)
    return StatsParser.parse_match(match.payload)

async def save_last_matches(last_matches: list[dict[str, Any]]):
    send_queue = []
    last_matches.reverse()
    for match in last_matches:
        if await MatchPayloadDAO.add(match):
            
            oMatch = StatsParser.parse_match(match)
            logger.info(f"Match {oMatch.matchStat.matchStartTime} {oMatch.playerStat.characterName.name} saved.")

            send_queue.append(oMatch)
    if last_matches:
        logger.info("All Available matches saved.")
            
    for obj in send_queue:
        await send_match_info_into_tg(obj)
        await asyncio.sleep(1)

class DBDIcons:
    killers = {
        "Chuckles": "5221958686020244903",
        "Bob": "5224606086681629564",
        "Spirit": "5222381997996941046",
        "Ghostface": "5222378192655913774",
        "HillBilly": "5222223719862143498",
        "Nurse": "5222155782069458165",
        "Shape": "5221935265563579295",
        "Witch": "5222100127883235669",
        "Killer07": "5222189519037567075",
        "Bear": "5224288834627341254",
        "Cannibal": "5222422744351673937",
        "Nightmare": "5222204169171013256",
        "Pig": "5222432236229397912",
        "Clown": "5222172197434461462",
        "Legion": "5222171823772307322",
        "Plague": "5222355510933624148",        
        "Demogorgon": "5222390669535907406",
        "Oni": "5222143124800836196",
        "Gunslinger": "5224651690644377445",
        "K20": "5222404761323605491",
        "K21": "5224517803628858360",               
        "K22": "5222058020023864787",
        "K23": "5222253024424009221",
        "K24": "5222312612800269230",
        "K25": "5222461334632826762",
        "K26": "5222077386031400199",
        "K27": "5222293891037829078",
        "K28": "5222088458457092274",
        "K29": "5222362447305807399",
        "K30": "5221950452567937471",
        "K31": "5221954713175495229",
        "K32": "5222328641618221785",
        "K33": "5224403621923293149",
        "K34": "5222118892595350773",
        "K35": "5222063032250699332",
        "K36": "5222146556479706244",
        "K37": "5222481001288076923",
        "K38": "5222429848227581213",
        "K39": "5222244387244773168",
        "K40": "5222383226357584091",
        "K41": "5222085344605804642",
        "K42": "5224223190347189636", # ЗАГЛУШКА
        "K43": "5224223190347189636", # ЗАГЛУШКА
    }
    survivors = {
        "Dwight": "5222139465488699483",
        "Meg": "5222035505805300564",
        "Claudette": "5222112905410940585",
        "Laurie": "5222030055491801528",
        "Nea": "5222225734201806498",
        "Jake": "5222119974927109592",
        "Feng": "5222323156944980100",
        "Bill": "5221933100900063573",
        "Ace": "5222007652942382748",
        "Eric": "5222194312221068550",
        "Smoke": "5224654478078151523",
        "Quentin": "5222075981577097065",
        "Adam": "5222128779610067276",
        "Kate": "5222000450282231876",
        "Jeff": "5222080675976352435",
        "Nancy": "5222087440549840947",
        "Steve": "5222297417205977456",
        "Jane": "5222425566145187250",
        "Ash": "5222324965126212594",        
        "Yui": "5224602590578250824",
        "Zarina": "5222102644734070422",
        "S22": "5222202876385860440",
        "S23": "5222293066404103723",
        "S24": "5222483939045705686",        
        "S26": "5222183188255774765",
        "S27": "5222422860315788834",
        "S28": "5222098817918212211",
        "S29": "5222242411559819870",
        "S30": "5221960189258796203",
        "S31": "5222169242496963472",
        "S32": "5224461621161659685",
        "S33": "5222235337748682663",
        "S34": "5221979628280779536",
        "S35": "5222057745145957933",
        "S36": "5221929385753349245",
        "S37": "5222354166608859943",
        "S38": "5222378789656367327",
        "S39": "5221972369786048494",
        "S40": "5222332494203884030",
        "S41": "5222186100243601763",
        "S42": "5224194100533694241",
        "S43": "5222313793916275960",
        "S44": "5222078528492703810",
        "S45": "5222303889721694478",
        "S47": "5221943541965559394",
        "S48": "5224738513408267237",
        "S49": "5224604463183993745",
    }

class CustomEmoji:
    def __init__(self, custom_emoji_id: int):
        self.custom_emoji_id = custom_emoji_id
    def __str__(self):
        return f'<tg-emoji emoji-id="{self.custom_emoji_id}"></tg-emoji>'

class DBDDicts:
    PlayerStatus = {
        "VE_Escaped": "ESCAPED",
        "VE_Sacrificed": "SACRIFICED",
        "VE_Disconnected": "DISCONNECTED",
        "VE_SurrenderLoss": "SURRENDER LOSS",
        "VE_Killed": "KILLED",
        "VE_SurrenderDraw": "SURRENDER DRAW",
        "VE_ManuallyLeftMatch": "MANUALLY LEFT MATCH"
    }

async def send_match_info_into_tg(match: ModelItem):
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
                        {"<br>".join([f"<a href=\"https://deadbydaylight.wiki.gg/wiki/{perk.name.replace(" ", "_")}\">{perk.name}</a>" for perk in opp.characterLoadout.perks])}
                    </blockquote>
                    <blockquote><h5>Power</h5><br>                   
                        <a href=\"https://deadbydaylight.wiki.gg/wiki/{opp.characterLoadout.power and opp.characterLoadout.power.name.replace(" ", "_") or "[NO URL]"}\">{opp.characterLoadout.power and opp.characterLoadout.power.name or "[NO POWER]"}</a><br>
                        {"<br>".join([f"+ <a href=\"https://deadbydaylight.wiki.gg/wiki/{addon.name.replace(" ", "_").replace("’", "%27").replace("‘", "%27")}\">{addon.name}</a>" for addon in opp.characterLoadout.addOns])}
                    </blockquote>
                    <blockquote><h5>Offering</h5><br>
                    <a href=\"https://deadbydaylight.wiki.gg/wiki/{opp.characterLoadout.offering and opp.characterLoadout.offering.name.replace(" ", "_") or "[NO URL]"}\">{opp.characterLoadout.offering and opp.characterLoadout.offering.name or "[NO OFFERING]"}</a>
                </details>
                """ for opp in match.opponentStat]
                )
            }         
        </details>
        '''
    if await bot.send_rich_message(chat_id=id, rich_message=InputRichMessage(html=text)):
        await bot.session.close()
        return True
    await bot.session.close()
    return False