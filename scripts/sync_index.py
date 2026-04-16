#!/usr/bin/env python3
"""Backwards-compatible wrapper around the canonical slide governance sync."""

from tools import slide_governance


def main() -> None:
    slide_governance.sync_repo(slide_governance.ROOT)
    print(
        "Synced manifest, legacy map, slide kinds, titles, agendas, viewer index, and footer page numbers"
    )


if __name__ == "__main__":
    main()
