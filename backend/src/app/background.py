import asyncio
import json
import logging

from app.services.event_processor_service import process_hourly_data_ready_event
from app.utils.redis import get_redis_client

logger = logging.getLogger(__name__)


async def redis_listener_task():
    """
    Background task that listens to the Redis 'fireguard_events' channel.
    When a HOURLY_DATA_READY event is received, it triggers the orchestration logic
    for MQTT alerts and ThingSpeak analytics.
    """
    logger.info("Starting Redis event listener task...")
    redis_client = await get_redis_client()
    pubsub = redis_client.pubsub()

    try:
        await pubsub.subscribe("fireguard_events")
        logger.info("Subscribed to 'fireguard_events' channel.")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"].decode("utf-8"))
                    event_type = data.get("event")

                    if event_type == "HOURLY_DATA_READY":
                        logger.info(
                            f"Received event: {event_type} at {data.get('timestamp')}"
                        )
                        # Process the event asynchronously so we don't
                        # block the listener loop
                        asyncio.create_task(process_hourly_data_ready_event())
                    else:
                        logger.debug(f"Received unknown event type: {event_type}")

                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON from Redis message.")
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")

    except asyncio.CancelledError:
        logger.info("Redis listener task cancelled.")
    except Exception as e:
        logger.error(f"Redis listener task failed: {e}")
    finally:
        await pubsub.unsubscribe("fireguard_events")
        logger.info("Unsubscribed from 'fireguard_events' channel.")
