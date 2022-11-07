from subscrape.db.subscrape_db import SubscrapeDB
import logging
import subscrape
import pytest

@pytest.mark.asyncio
async def test_fetch_extrinsics_list():
    
    extrinsic_idx = "14238250-2"
    
    config = {
        "kusama":{
            "extrinsics-list":[
                extrinsic_idx
            ],
        }
    }

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("wiping storage")
    subscrape.wipe_cache()
    logging.info("scraping")
    await subscrape.scrape(config)
    logging.info("testing")

    db = SubscrapeDB()
    extrinsic = db.read_extrinsic(extrinsic_idx)

    assert extrinsic is not None
    assert extrinsic.extrinsic_hash == '0x408aacc9a42189836d615944a694f4f7e671a89f1a30bf0977a356cf3f6c301c'
    assert type(extrinsic.params) is list
    
    db.close()



@pytest.mark.asyncio
@pytest.mark.parametrize("auto_hydrate", [True, False])
async def test_fetch_and_hydrate_extrinsic(auto_hydrate):

    config = {
        "kusama":{
            "_auto_hydrate": auto_hydrate,
            "extrinsics": None,
            "_params": {
                "block_num": 15228214
            }
        }
    }
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logging.info("wiping storage")
    subscrape.wipe_cache()
    logging.info("scraping")
    await subscrape.scrape(config)
    logging.info("testing")

    db = SubscrapeDB()
    extrinsic = db.read_extrinsic("15228214-2")
    assert extrinsic is not None, "This extrinsic should exist in the database"
    assert extrinsic.extrinsic_hash == '0x8863fb33e2bac6f48b8a0c6a08a27871631046a2654fcd4574f4e8faaaa7cba1'
    if auto_hydrate:
        assert extrinsic.params is not None, "Hydrated extrinsic should have params"
    else:
        assert extrinsic.params is None, "Non-hydrated extrinsic should not have params"
    db.close()


@pytest.mark.asyncio
async def test_fetch_extrinsics_by_module_call():
        
    config = {
        "kusama":{
            "_auto_hydrate": False,
            "extrinsics":{
                "bounties": ["propose_bounty"]
            }
        }
    }
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logging.info("wiping storage")
    subscrape.wipe_cache()
    logging.info("scraping")
    scrape_result = await subscrape.scrape(config)
    logging.info("testing")

    db = SubscrapeDB()
    extrinsics = db.extrinsics_query("bounties", "propose_bounty").all()

    extrinsics = [e for e in extrinsics if e.id == "14061443-2"]
    assert len(extrinsics) == 1, "Expected 1 extrinsic"
    extrinsic = extrinsics[0]
    assert extrinsic.extrinsic_hash == '0x9f2a81d8d92884122d122d806276da7ff9b440a0a273bc3898cbd4072d5f62e1'
    
    db.close()

@pytest.mark.asyncio
async def test_fetch_extrinsics_by_module():
    
    config = {
        "kusama":{
            "_auto_hydrate": False,
            "extrinsics":{
                "bounties": None
            }
        }
    }
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logging.info("wiping storage")
    subscrape.wipe_cache()
    logging.info("scraping")
    await subscrape.scrape(config)
    logging.info("testing")

    db = SubscrapeDB()

    extrinsics = db.extrinsics_query("bounties", "propose_bounty")
    extrinsics = [e for e in extrinsics if e.id == "12935940-3"]
    assert len(extrinsics) == 1, "Expected 1 extrinsic"
    extrinsic = extrinsics[0]
    assert extrinsic.extrinsic_hash == '0x28b3e9dc097036a98b43b9792745be89d3fecbbca71200b45a2aba901c7cc5af'

    extrinsics = db.extrinsics_query("bounties", "extend_bounty_expiry")
    extrinsics = [e for e in extrinsics if e.id == "14534356-3"]
    assert len(extrinsics) == 1, "Expected 1 extrinsic"
    extrinsic = extrinsics[0]
    assert extrinsic.extrinsic_hash == '0xf02b930789a35b4b942006c60ae6c83daee4d87237e213bab4ce0e7d93cfb0f4'

    db.close()

@pytest.mark.asyncio
async def test_fetch_extrinsics_by_address():
    
    config = {
        "kusama":{
            "_auto_hydrate": False,
            "extrinsics": None,
            "_params": {
                "address": "EGP7XztdTosm1EmaATZVMjSWujGEj9nNidhjqA2zZtttkFg"
            }
        }
    }
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logging.info("wiping storage")
    subscrape.wipe_cache()
    logging.info("scraping")
    await subscrape.scrape(config)
    logging.info("testing")

    db = SubscrapeDB()
    extrinsic = db.read_extrinsic("14815834-2")
    assert extrinsic is not None, "This extrinsic should exist in the database"
    assert extrinsic.extrinsic_hash == '0xc015e661ce5a763d2377d5216037677f5e16fe1a5ec4471de3acbd6be683461b'

    db.close()
