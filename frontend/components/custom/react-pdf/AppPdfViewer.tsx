'use client'

import { RPProvider, RPDefaultLayout, RPPages } from '@pdf-viewer/react'

interface AppPdfViewerProps {
  fileUrl: string;
}

const AppPdfViewer = ({ fileUrl }: AppPdfViewerProps) => {
  return (
    <RPProvider src={fileUrl}>
      <RPDefaultLayout>
        <RPPages />
      </RPDefaultLayout>
    </RPProvider>
  )
}

export default AppPdfViewer

