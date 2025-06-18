// AudioWorkletProcessor for PCM conversion
class PCMProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const channelData = input[0]; // モノラル音声を使用
            if (channelData && channelData.length > 0) {
                // Float32ArrayをInt16Arrayに変換（PCM 16bit）
                const pcmData = new Int16Array(channelData.length);
                for (let i = 0; i < channelData.length; i++) {
                    // -1.0 から 1.0 の範囲を -32768 から 32767 の範囲に変換
                    pcmData[i] = Math.max(-32768, Math.min(32767, channelData[i] * 32767));
                }
                
                // メインスレッドにPCMデータを送信
                this.port.postMessage({
                    type: 'pcm-data',
                    data: pcmData.buffer
                });
            }
        }
        return true;
    }
}

registerProcessor('pcm-processor', PCMProcessor);