import websocket
import wave
import time
import os

def test_mantenimiento_voz():
    # Asegúrate de usar el archivo que pasaste por FFmpeg
    audio_file = "aviso_prueba_final.wav" 
    url = "ws://localhost:8080/audio-stream"

    if not os.path.exists(audio_file):
        print(f"❌ Error: No encuentro el archivo {audio_file}")
        return

    try:
        ws = websocket.create_connection(url)
        print("🟢 Conectado al Backend en Zacatelco")

        with wave.open(audio_file, 'rb') as wf:
            # Validamos el formato en tiempo de ejecución
            print(f"Propiedades: {wf.getnchannels()} canales, {wf.getframerate()}Hz")
            
            # Leemos fragmentos de 1600 bytes
            data = wf.readframes(800) # 800 frames * 2 bytes = 1600 bytes
            while len(data) > 0:
                ws.send_binary(data)
                data = wf.readframes(800)
                # Pausa mínima para simular el ritmo del habla humana
                time.sleep(0.01)

        print("✅ Audio enviado. Esperando procesamiento...")
        time.sleep(1) 
        ws.close()
        print("🔒 Conexión cerrada.")

    except Exception as e:
        print(f"❌ Error técnico: {e}")

if __name__ == "__main__":
    test_mantenimiento_voz()