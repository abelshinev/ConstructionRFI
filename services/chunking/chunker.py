import re #regex
from dataclasses import dataclass
from typing import Any

# a dataclass creates class -> __init__(self, var) automatically
@dataclass
class ChunkPayload:
    chunk_idx: int
    text: str
    chunk_type: str
    chunk_metadata: dict[str, Any]


def build_chunks(extracted_content: dict[str, Any], asset_content_type: str) -> list[ChunkPayload]:
    if asset_content_type.startswith("audio/"):
        return chunk_audio_transcript(extracted_content)

    if asset_content_type == "application/pdf":
        return chunk_pdf_text(extracted_content)

    return chunk_plain_text(extracted_content)

def build_chunks_from_worker_result(worker_result: dict[str, Any]) -> list[ChunkPayload]:
    worker_type = worker_result.get("worker_type")
    data = worker_result.get("data") or {}

    if worker_type == "pdf-data":
        return chunk_pdf_text(data)

    if worker_type == "speech-transcript":
        return chunk_audio_transcript(data)

    return []


# Plain Text

def get_text(extracted_content: dict[str, Any]) -> str:
    return (
        extracted_content.get("text") or extracted_content.get("transcript") or ""
    ).strip()


def chunk_plain_text(extracted_content: dict[str, Any]) -> list[ChunkPayload]:
    text = get_text(extracted_content)
    paragraphs = split_paragraphs(text)

    return [
        ChunkPayload(
            chunk_idx=index,
            text=paragraph,
            chunk_type="paragraph",
            chunk_metadata={"source": extracted_content.get("source")},
        )
        for index, paragraph in enumerate(paragraphs)
    ]


# PDFS

def split_paragraphs(text: str) -> list[str]:
    return [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n+", text)
        if paragraph.strip()
    ]


def chunk_pdf_text(extracted_content: dict[str, Any]) -> list[ChunkPayload]:
    text = get_text(extracted_content)
    paragraphs = split_paragraphs(text)

    return [
        ChunkPayload(
            chunk_idx=index,
            text=paragraph,
            chunk_type="page_section",
            chunk_metadata={
                "source": extracted_content.get("source"),
                "pages": extracted_content.get("pages"),
                "page_count": extracted_content.get("page_count"),
            },
        )
        for index, paragraph in enumerate(paragraphs)
    ]


# Audio
def group_segments(segments: list[dict[str, Any]], group_size: int) -> list[list[dict[str, Any]]]:
    return [
        segments[index:index + group_size]
        for index in range(0, len(segments), group_size)
    ]

# we chunk on the basis of timestamps here (subject to change)

def chunk_audio_transcript(extracted_content: dict[str, Any]) -> list[ChunkPayload]:
    segments = extracted_content.get("segments") or []

    if not segments:
        text = get_text(extracted_content)
        return [
            ChunkPayload(
                chunk_idx=0,
                text=text,
                chunk_type="transcript_instruction",
                chunk_metadata={"source": extracted_content.get("source")},
            )
        ] if text else []

    chunks = []

    for index, segment_group in enumerate(group_segments(segments, group_size=3)):
        text = " ".join(segment.get("text", "").strip() for segment in segment_group).strip()

        if not text:
            continue

        chunks.append(
            ChunkPayload(
                chunk_idx=index,
                text=text,
                chunk_type="transcript_instruction",
                chunk_metadata={
                    "source": extracted_content.get("source"),
                    "start": segment_group[0].get("start"),
                    "end": segment_group[-1].get("end"),
                    "segment_ids": [segment.get("id") for segment in segment_group],
                },
            )
        )

    return chunks
