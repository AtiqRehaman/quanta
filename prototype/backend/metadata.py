# -------------------------------
# Generate Metadata
# -------------------------------

def metadata(blocks, top_blocks, block_size=16):

    metadata = []

    # Quantum blocks
    for _, i, j in top_blocks:
        metadata.append({
            "row": i,
            "col": j,
            "type": "quantum"
        })

    # Classical blocks
    all_blocks = [(i,j) for i in range(blocks.shape[0]) for j in range(blocks.shape[1])]
    for i,j in all_blocks:
        if (i,j) not in [(x["row"], x["col"]) for x in metadata]:
            metadata.append({
                "row": i,
                "col": j,
                "type": "classical"
            })

    metadata_info = {
        "block_size": block_size,
        "top_percentage": 15
    }

    metadata_full = {"blocks": metadata, "info": metadata_info}
    return metadata_full