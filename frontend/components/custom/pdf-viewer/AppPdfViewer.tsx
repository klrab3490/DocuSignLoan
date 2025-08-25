'use client'

import { RPProvider, RPDefaultLayout, RPPages } from '@pdf-viewer/react'

interface AppPdfViewerProps {
  fileUrl: string;
  initialPage?: number;
}


const AppPdfViewer = ({ fileUrl, initialPage = 1 }: AppPdfViewerProps) => {
  return (
    <RPProvider src={fileUrl} initialPage={initialPage}>
      <RPDefaultLayout>
        <RPPages />
      </RPDefaultLayout>
    </RPProvider>
  )
}

export default AppPdfViewer

