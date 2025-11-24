// frontend/src/components/PhotoGallery.jsx
import React, { useState, useEffect } from "react";
import "./PhotoGallery.css";

export default function PhotoGallery({ photos = [], destination = "" }) {
    const [selectedPhoto, setSelectedPhoto] = useState(null);

    // Handle ESC key to close lightbox
    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === "Escape" && selectedPhoto) {
                setSelectedPhoto(null);
            }
        };
        window.addEventListener("keydown", handleEsc);
        return () => window.removeEventListener("keydown", handleEsc);
    }, [selectedPhoto]);

    // Prevent body scroll when lightbox is open
    useEffect(() => {
        if (selectedPhoto) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "unset";
        }
        return () => {
            document.body.style.overflow = "unset";
        };
    }, [selectedPhoto]);

    if (!photos || photos.length === 0) return null;

    return (
        <>
            <div className="photo-gallery-container">
                <h4 className="gallery-header">
                    <span style={{ fontSize: "24px" }}>📸</span>
                    <span>{destination} Gallery</span>
                </h4>

                <div className="gallery-grid">
                    {photos.map((photo, idx) => (
                        <div
                            key={idx}
                            className="photo-card"
                            onClick={() => setSelectedPhoto(photo)}
                        >
                            <img
                                src={photo.url}
                                alt={photo.alt || `${destination} photo ${idx + 1}`}
                                className="photo-img"
                            />
                            <div className="photo-overlay">
                                📷 {photo.photographer}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {selectedPhoto && (
                <div
                    className="lightbox-overlay"
                    onClick={() => setSelectedPhoto(null)}
                >
                    <div
                        className="lightbox-content"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <button
                            className="lightbox-close"
                            onClick={() => setSelectedPhoto(null)}
                            aria-label="Close"
                        >
                            ✕
                        </button>

                        <img
                            src={selectedPhoto.url}
                            alt={selectedPhoto.alt}
                            className="lightbox-img"
                        />

                        <div className="lightbox-caption">
                            <div className="caption-title">
                                {selectedPhoto.alt || destination}
                            </div>
                            <div className="caption-credit">
                                Photo by <strong>{selectedPhoto.photographer}</strong> • {selectedPhoto.source}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
