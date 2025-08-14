import React from 'react';
import { Separator } from "@/components/ui/separator"
import { ModeToggle } from '@/components/theme/mode-toggle';

// type Props = {}

// export default function Navbar({}: Props) {
export default function Navbar() {
  return (
    <div className='flex justify-between w-full p-2'>
        <div>Admin Panel</div>
        <div className='flex items-center'>
            <div>Item 1</div>
            <Separator orientation="vertical" className='h-6 mx-2' />
            <div>Item 2</div>
            <Separator orientation="vertical" className='h-6 mx-2' />
            <div>Item 3</div>
            <Separator orientation="vertical" className='h-6 mx-2' />
            <ModeToggle />
        </div>
    </div>
  )
}