import os
import requests
import datetime
import random

from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from voice.voice import Voice
from voice.audio_convert import any_to_mp3


class FlashTTSVoice(Voice):
    def voiceToText(self, voice_file):
        """
        FlashTTS 当前仅支持合成，不支持语音转文字。
        """
        logger.debug(f"[FlashTTS VOICE] voiceToText 不支持，voice_file={voice_file}")
        return Reply(ReplyType.ERROR, "当前语音引擎不支持语音转文字，请稍后重试~")

    def textToVoice(self, text: str):
        logger.debug(f"[FlashTTS VOICE] text={text}")
        try:
            # 确保输出目录存在
            os.makedirs("tmp", exist_ok=True)

            # 构造请求参数
            data = {
                "model": "spark",
                "input": text,
                "voice": conf().get("flashtts_voice"),
                "response_format": "mp3",
                "stream": False
            }
            headers = {
                "Content-Type": "application/json"
            }
            base_url = conf().get("flashtts_base")
            url = f"{base_url.rstrip('/')}/v1/audio/speech"

            # 发送请求
            response = requests.post(url, json=data, headers=headers)
            if response.status_code != 200:
                logger.error(f"[FlshTTS VOICE] 非200响应: {response.status_code} {response.text}")
                response.raise_for_status()

            # 生成文件名并保存
            file_name = "tmp/" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 1000)) + ".mp3"
            with open(file_name, 'wb') as f:
                f.write(response.content)

            logger.info(f"[FlshTTS VOICE] textToVoice success, file_name={file_name}")
            return Reply(ReplyType.VOICE, file_name)

        except Exception as e:
            logger.error(f"[FlshTTS VOICE] textToVoice 错误: {e}", exc_info=True)
            return Reply(ReplyType.ERROR, "合成语音时遇到问题，请稍后再试~")
