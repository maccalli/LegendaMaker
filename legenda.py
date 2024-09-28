import moviepy.editor as mp
import whisper
import os
import shutil

def extract_audio_from_video(video_file, output_audio_file="audio.wav"):
    """Extrai o áudio do vídeo e o salva como arquivo WAV"""
    video = mp.VideoFileClip(video_file)
    video.audio.write_audiofile(output_audio_file)
    return video.duration

def transcribe_with_whisper(audio_file):
    """Transcreve o áudio usando a biblioteca Whisper"""
    model = whisper.load_model("base")  # Você pode usar outros tamanhos de modelo, como "small", "medium", "large"
    result = model.transcribe(audio_file)
    return result['text']

def seconds_to_timecode(seconds):
    """Converte tempo em segundos para formato de timecode SRT"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

def generate_srt(transcription, total_duration, output_srt_file="output.srt"):
    """Gera o arquivo SRT a partir da transcrição"""
    lines = transcription.split(". ")
    subs = []

    avg_duration_per_line = total_duration / len(lines)  # Tempo médio por linha

    start_time = 0  # Inicializando o tempo
    for index, line in enumerate(lines):
        # Define o tempo de início e fim da legenda
        end_time = start_time + avg_duration_per_line
        subs.append({
            'index': index + 1,
            'start': seconds_to_timecode(start_time),
            'end': seconds_to_timecode(end_time),
            'text': line.strip()
        })
        start_time = end_time  # Atualiza o tempo de início para a próxima legenda

    # Salva o arquivo SRT
    with open(output_srt_file, "w", encoding='utf-8') as f:
        for sub in subs:
            f.write(f"{sub['index']}\n{sub['start']} --> {sub['end']}\n{sub['text']}\n\n")
    print(f"Arquivo SRT salvo como {output_srt_file}")

def main():
    # Solicitar o caminho do arquivo de vídeo ao usuário
    video_file = input("Digite o caminho do arquivo de vídeo: ")

    # Verificar se o arquivo existe
    if not os.path.exists(video_file):
        print("Arquivo não encontrado. Verifique o caminho e tente novamente.")
        return
    
    # Criar um nome de pasta baseado no nome do arquivo de vídeo (sem extensão)
    project_name = os.path.splitext(os.path.basename(video_file))[0]
    project_folder = os.path.join(os.path.dirname(video_file), project_name)

    # Criar a pasta do projeto, se não existir
    os.makedirs(project_folder, exist_ok=True)

    # Extrair áudio do vídeo e obter a duração total
    audio_file = os.path.join(project_folder, "audio.wav")
    total_duration = extract_audio_from_video(video_file, audio_file)

    # Transcrever áudio para texto
    transcription = transcribe_with_whisper(audio_file)
    
    if transcription:
        # Gerar arquivo SRT com tempos automáticos
        srt_file = os.path.join(project_folder, f"{project_name}.srt")
        generate_srt(transcription, total_duration, srt_file)

    # Copiar o arquivo de vídeo para a pasta do projeto
    shutil.copy(video_file, project_folder)

    # Remover o arquivo de áudio temporário
    os.remove(audio_file)

if __name__ == "__main__":
    main()