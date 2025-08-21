"use client";

import { useState, useEffect } from "react";
import { pdfjs, Document, Page } from "react-pdf";

type Highlight = {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
};

interface HighlightedPDFPageProps {
    fileUrl: string;          // PDF file URL
    pageNumber?: number;       // which page to render
    highlights?: Highlight[];  // bounding boxes from backend
    scale?: number;           // zoom scale
}

export default function HighlightedPDFPage({
    fileUrl,
    pageNumber,
    highlights,
    scale = 1.5,
}: HighlightedPDFPageProps) {
    const [pageDims, setPageDims] = useState<{ width: number; height: number }>();

    // Configure PDF.js worker only in browser
    useEffect(() => {
        if (typeof window !== "undefined" && pdfjs.GlobalWorkerOptions) {
            pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;
        }
    }, []);

    return (
        <div className="relative inline-block">
            <Document file={fileUrl}>
                <Page
                    pageNumber={pageNumber}
                    scale={scale}
                    onLoadSuccess={(page) =>
                        setPageDims({ width: page.width * scale, height: page.height * scale })
                    }
                />
            </Document>

            {pageDims && (
                <div
                    className="absolute top-0 left-0"
                    style={{ width: pageDims.width, height: pageDims.height }}
                >
                    {highlights?.map((r, i) => (
                        <div
                            key={i}
                            className="absolute bg-yellow-400 opacity-50 rounded"
                            style={{
                                left: r.x0 * scale,
                                top: r.y0 * scale,
                                width: (r.x1 - r.x0) * scale,
                                height: (r.y1 - r.y0) * scale,
                            }}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
