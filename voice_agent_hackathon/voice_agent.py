#
# Copyright (c) 2024, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import aiohttp
import os
import sys

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.services.openai import OpenAILLMContext, OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport

from openai.types.chat import ChatCompletionToolParam

from runner import configure

from loguru import logger

from dotenv import load_dotenv

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")



###
###
# Functions calls to Mock the tool calls of a CS agent 
###

def get_product_details_func(product_name):
    # Placeholder for API call to retrieve product details
    return {"key_features": "A15 Bionic chip, 5G support, has Apple Intelligent Assistant", "price": "$799"}

def get_warranty_status_func(device_id):
    logger.debug(f"Checking warranty status for device_id: {device_id}")
    if len(device_id) % 2 == 0:
        return "under warranty"
    else:
        return "not under warranty"
    
def handle_product_speculation_func() -> str:
    return "I'm afraid I can't comment on products we haven't officially announced yet. However, I'd be happy to discuss our current lineup and help you find the right fit for your needs."

def initiate_repair_or_replacement_func(device_id: str) -> dict:
    logger.info(f"Initiating repair or replacement process for device_id: {device_id} ...")
    return "I've initiated a repair through our service center. Please bring your device to the nearest Apple Store. A normal repair process takes about 3~5 business days."

def get_paid_repair_options_func(device_id: str, issue_description: str) -> dict:
    return {"cost": "$199"}

def handle_hardware_repair_func(device_id: str, is_covered: bool, issue_description: str) -> str:
    if is_covered:
        return f"I understand your concern about your {issue_description}. Since your product is covered under warranty, I can initiate a repair through our service center. Do you want me to start the process?"
    else:
        repair_options = get_paid_repair_options_func(device_id, issue_description)
        return f"Unfortunately, your {issue_description} is out of warranty. However, I can offer you a paid repair option for {repair_options['cost']}. Do you want me to start the process?"

def give_common_troubleshooting_steps_func(issue_description: str) -> str:
    return f"Let's try a few common troubleshooting steps to resolve your issue with {issue_description}. You can try to restart your device, update the software, or reset the settings to factory defaults."

def get_billing_details_func(account_id: str) -> dict:
    return {"amount": "$9.99", "date": "2024-10-15", "service": "Apple Music"}

def cancel_subscription_func(account_id: str, subscription_type: str):
    logger.info(f"Canceling subscription for account_id: {account_id} and subscription_type: {subscription_type} ...")
    return f"Your {subscription_type} has been canceled successfully you can still use that service until the end of the billing cycle."

def get_billing_cycle_end_date_func(account_id: str, subscription_type: str) -> str:
    return "2024-11-15"

async def get_latest_apple_product_info(function_name, tool_call_id, args, llm, context, result_callback):
    product_details = get_product_details_func(args["product_name"])
    await result_callback(product_details)


async def get_warranty_status(function_name, tool_call_id, args, llm, context, result_callback):
    status = get_warranty_status_func(args["device_id"])
    await result_callback({"warranty_status": status})

async def get_paid_repair_options(function_name, tool_call_id, args, llm, context, result_callback):
    resp = get_paid_repair_options_func(args["device_id"], args["issue_description"])
    await result_callback(resp)

async def handle_hardware_repair_request(function_name, tool_call_id, args, llm, context, result_callback):
    resp = handle_hardware_repair_func(args["device_id"], args["is_covered"], args["issue_description"])
    await result_callback({"response": resp})


async def initiate_repair_or_replacement_process(function_name, tool_call_id, args, llm, context, result_callback):
    resp = initiate_repair_or_replacement_func(args["device_id"])
    await result_callback({"response": resp})

async def give_common_troubleshooting_steps(function_name, tool_call_id, args, llm, context, result_callback):
    resp = give_common_troubleshooting_steps_func(args["issue_description"])
    await result_callback({"response": resp})

async def get_billing_details(function_name, tool_call_id, args, llm, context, result_callback):
    resp = get_billing_details_func(args["account_id"])
    await result_callback(resp)

async def cancel_subscription(function_name, tool_call_id, args, llm, context, result_callback):
    resp = cancel_subscription_func(args["account_id"], args["subscription_type"])
    await result_callback({"response": resp})

async def get_billing_cycle_end_date(function_name, tool_call_id, args, llm, context, result_callback):
    resp = get_billing_cycle_end_date_func(args["account_id"], args["subscription_type"])
    await result_callback({"response": resp})


async def handle_product_speculation(function_name, tool_call_id, args, llm, context, result_callback):
    resp = handle_product_speculation_func()
    await result_callback({"response": resp})



async def main():
    async with aiohttp.ClientSession() as session:
        (room_url, token) = await configure(session)

        transport = DailyTransport(
            room_url,
            token,
            "Respond bot",
            DailyParams(
                audio_out_enabled=True,
                transcription_enabled=True,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )

        tts = CartesiaTTSService(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",  # British Lady
        )

        llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
        # Register a function_name of None to get all functions
        # sent to the same callback with an additional function_name parameter.
        llm.register_function('get_latest_apple_product_info', get_latest_apple_product_info)
        llm.register_function('get_warranty_status', get_warranty_status)
        llm.register_function('get_paid_repair_options', get_paid_repair_options)
        llm.register_function('handle_hardware_repair_request', handle_hardware_repair_request)
        llm.register_function('initiate_repair_or_replacement_process', initiate_repair_or_replacement_process)
        llm.register_function('give_common_troubleshooting_steps', give_common_troubleshooting_steps)
        llm.register_function('get_billing_details', get_billing_details)
        llm.register_function('cancel_subscription', cancel_subscription)
        llm.register_function('get_billing_cycle_end_date', get_billing_cycle_end_date)
        llm.register_function('handle_product_speculation', handle_product_speculation)
        tools = [
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "get_warranty_status",
                    "description": "Determine the warranty status of a device based on its ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "The unique identifier of the customer's device."
                            }
                        },
                        "required": ["device_id"],
                        "additionalProperties": False
                    },
                },
            ),
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "get_latest_apple_product_info",
                    "description": "Get the latest info about an Apple product",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {
                                "type": "string",
                                "description": "The product name, e.g. iPhone 15",
                            }
                        },
                        "required": ["product_name"],
                    },
                },
            ),
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "handle_hardware_repair_request",
                    "description": "Handle a device repair request",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "The unique identifier of the customer's device."
                            },
                            "is_covered": {
                                "type": "boolean",
                                "description": "if the device is under warranty or not."
                            },  
                            "issue_description": {
                                "type": "string",
                                "description": "A description of the issue reported by the customer."
                            }
                        },
                        "required": ["device_id", "is_covered", "issue_description"],
                    },
                }
            ),
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "get_paid_repair_options",
                    "description": "Get the paid repair options for a device",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "The unique identifier of the customer's device."
                            },
                            "issue_description": {
                                "type": "string",
                                "description": "A description of the issue reported by the customer."
                            }
                        },
                        "required": ["device_id", "issue_description"],
                    },
                }
            ),
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "initiate_repair_or_replacement_process",
                    "description": "Initiate a repair or replacement process for a device",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "The unique identifier of the customer's device."
                            }
                        },
                        "required": ["device_id"],
                    },
                }
            ),
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "give_common_troubleshooting_steps",
                    "description": "Give common troubleshooting steps for a software issue like battery draining, slow performance, black screen, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "issue_description": {
                                "type": "string",
                                "description": "A description of the issue reported by the customer."
                            }
                        },
                        "required": ["issue_description"],
                    },
                }
            ),
            ChatCompletionToolParam(
                type="function",
                function={ 
                    "name": "get_billing_details",
                    "description": "Get the latest billing information for a customer's account",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "account_id": {
                                "type": "string",
                                "description": "The unique identifier of the customer's account."
                            }
                        },
                        "required": ["account_id"],
                    },
                }
            ),
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "cancel_subscription",
                    "description": "Cancel a customer's subscription",  
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "account_id": {
                                "type": "string",
                                "description": "The unique identifier of the customer's account."
                            },
                            "subscription_type": {
                                "type": "string",
                                "description": "The type of subscription to be canceled."
                            }
                        },
                        "required": ["account_id", "subscription_type"],
                    },  
                }
            ),
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "get_billing_cycle_end_date",
                    "description": "Get the end date of the billing cycle for a subscription",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "account_id": {
                                "type": "string",
                                "description": "The unique identifier of the customer's account."
                            },
                            "subscription_type": {  
                                "type": "string",
                                "description": "The type of subscription to get the billing cycle end date for."
                            }
                        },
                        "required": ["account_id", "subscription_type"],
                    },
                }
            ), 
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "handle_product_speculation",
                    "description": "Handle product speculation inquiries by declining to comment on unannounced products.",
                    "parameters": {},
                }
            ),
        ]
        messages = [
            {
                "role": "system",
                "content": "You are a helpful Apple customer support agent. Your goal is to demonstrate your capabilities in a succinct way. Your output will be converted to audio so don't include special characters in your answers. Respond to what the user said in a creative and helpful way. Start the conversation with 'Hello, I am an AI customer support agent from Apple, how can I help you today?'",
            },
        ]

        context = OpenAILLMContext(messages, tools)
        context_aggregator = llm.create_context_aggregator(context)

        pipeline = Pipeline(
            [
                transport.input(),
                context_aggregator.user(),
                llm,
                tts,
                transport.output(),
                context_aggregator.assistant(),
            ]
        )

        task = PipelineTask(
            pipeline,
            PipelineParams(
                allow_interruptions=True,
                enable_metrics=True,
                enable_usage_metrics=True,
                report_only_initial_ttfb=True,
            ),
        )

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            transport.capture_participant_transcription(participant["id"])
            # Kick off the conversation.
            await task.queue_frames([context_aggregator.user().get_context_frame()])

        runner = PipelineRunner()

        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
