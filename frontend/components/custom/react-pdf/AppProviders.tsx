'use client'
import { type PropsWithChildren } from 'react'
import { RPConfig, RPConfigProps } from '@pdf-viewer/react'

function AppProviders({ children, ...props }: PropsWithChildren<RPConfigProps>) {
    return (
      <RPConfig {...props}>
        {children}
      </RPConfig>
    )
}
export default AppProviders
