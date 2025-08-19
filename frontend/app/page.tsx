"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Save, Upload, FileText, Search, Database } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

type JobResult = {
    job_id: string
    status: string
    filename: string
    result: RawResult
}

type RawResult = {
    dates: {
        agreement_date?: RawField
        effective_date?: RawField
        maturity_date?: RawField
        [key: string]: RawField | undefined
    }
    general?: {
        borrower?: RawField
        agent?: RawField
        security_agent?: RawField
        sponsor_name?: RawField
        majority_lenders?: RawField
        [key: string]: RawField | undefined
    }
    definitions?: Record<string, RawField>
    credit_facilities?: Record<string, RawField>
    representations_and_warranties?: Record<string, RawField>
    covenants?: Record<string, RawField>
    defaults?: Record<string, RawField>
    miscellaneous?: Record<string, RawField>
}

type RawField = {
    value: string | null
    page_number: number
}

// Status
type JobSummary = {
    job_id: string
    status: string
    filename: string
}

export default function Home() {
    const [file, setFile] = useState<File | null>(null)
    const [status, setStatus] = useState<string | null>(null)
    const [fetching, setFetching] = useState<boolean>(false)
    const [jobID, setJobID] = useState<string | null>(null)
    const [result, setResult] = useState<JobResult | null>(null)
    const [editableData, setEditableData] = useState<RawResult | null>(null)
    const [isEditing, setIsEditing] = useState(false)
    const [jobs, setJobs] = useState<JobSummary[] | null>([])
    const [fetchStatus, setFetchStatus] = useState<string | null>(null)

    const handleUpload = async () => {
        setStatus("Uploading")
        if (!file) {
            setStatus("No file selected")
            return
        }

        const formData = new FormData()
        formData.append("file", file)

        try {
            const result = await fetch("http://localhost:8000/pdf/extract-and-format/", {
                method: "POST",
                body: formData,
            })

            if (!result.ok) {
                setStatus("Upload failed")
                return
            }

            const data = await result.json()
            setJobID(data.job_id)
            setStatus("Upload successful")
        } catch (error) {
            setStatus("Error uploading")
            console.error(error)
        }
    }

    const fetchJobs = async () => {
        setFetchStatus("Fetching data...")

        try {
            const result = await fetch("http://localhost:8000/pdf/status/")
            if (!result.ok) throw new Error("Failed to fetch data")
            const data = await result.json()
            setJobs(data)
            console.log("Fetched jobs:", data);
        } catch (error) {
            console.error(error)
            throw error
        } finally {
            setFetchStatus("Fetched Successfully")
        }
    }

    const getData = async (id: string) => {
        setFetching(true)
        if (!id) return

        try {
            const result = await fetch(`http://localhost:8000/pdf/jobs/${id}`)
            if (!result.ok) throw new Error("Failed to fetch data")
            const data = await result.json()

            setResult(data)
            setEditableData(data.result)
        } catch (error) {
            console.error(error)
        } finally {
            setFetching(false)
        }
    }

    const handleEditToggle = () => {
        setIsEditing(!isEditing)
        if (!isEditing && result) {
            setEditableData({ ...result.result })
        }
    }

    const handleSave = () => {
        console.log("Saving data:", editableData)
        setIsEditing(false)
        if (result && editableData) {
            setResult({ ...result, result: editableData })
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-muted/30 to-muted/50 p-4 md:p-6">
            <div className="max-w-6xl mx-auto space-y-8">
                <div className="text-center space-y-2 mb-8">
                    <h1 className="text-3xl md:text-4xl font-bold text-foreground">PDF Document Processor</h1>
                    <p className="text-muted-foreground text-lg">Extract, analyze, and manage agreement data with ease</p>
                </div>

                {!jobID && !result && (
                    <Card className="w-full max-w-2xl mx-auto shadow-lg border-0 bg-card/80 backdrop-blur-sm">
                        <CardHeader className="text-center pb-4">
                            <CardTitle className="text-2xl font-semibold text-card-foreground flex items-center justify-center gap-2">
                                <Database className="w-6 h-6 text-primary" />
                                Document Processing Hub
                            </CardTitle>
                            <p className="text-muted-foreground">Upload a new PDF document or retrieve existing processed data</p>
                        </CardHeader>
                        <CardContent className="pt-2">
                            <Tabs defaultValue="upload" className="w-full">
                                <TabsList className="grid w-full grid-cols-2 mb-6 bg-muted/50">
                                    <TabsTrigger
                                        value="upload"
                                        className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
                                    >
                                        <Upload className="w-4 h-4" />
                                        Upload Document
                                    </TabsTrigger>
                                    <TabsTrigger
                                        value="fetch"
                                        className="flex items-center gap-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
                                    >
                                        <Search className="w-4 h-4" />
                                        Retrieve Data
                                    </TabsTrigger>
                                </TabsList>

                                <TabsContent value="upload" className="space-y-6">
                                    <div className="text-center mb-6">
                                        <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                                            <Upload className="w-8 h-8 text-primary" />
                                        </div>
                                        <h3 className="text-lg font-semibold text-card-foreground mb-2">Upload PDF Document</h3>
                                        <p className="text-sm text-muted-foreground">Select a PDF file to extract agreement data</p>
                                    </div>
                                    <div className="space-y-4">
                                        <div>
                                            <Label htmlFor="pdf-upload" className="text-sm font-medium text-card-foreground">
                                                PDF Document
                                            </Label>
                                            <Input
                                                id="pdf-upload"
                                                type="file"
                                                accept="application/pdf"
                                                onChange={(e) => setFile(e.target.files?.[0] || null)}
                                                className="mt-2 border-2 border-dashed border-border hover:border-primary/50 transition-colors"
                                            />
                                        </div>
                                        <Button
                                            onClick={(e) => {
                                                e.preventDefault()
                                                handleUpload()
                                            }}
                                            className="w-full h-12 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
                                            disabled={!file || status === "Uploading"}
                                        >
                                            {status === "Uploading" ? (
                                                <>
                                                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin mr-2" />
                                                    Processing Document...
                                                </>
                                            ) : (
                                                <>
                                                    <Upload className="w-4 h-4 mr-2" />
                                                    Upload & Process PDF
                                                </>
                                            )}
                                        </Button>
                                        {status && (
                                            <div className="text-center">
                                                <Badge
                                                    variant={
                                                        status.includes("successful")
                                                            ? "default"
                                                            : status.includes("failed") || status.includes("Error")
                                                                ? "destructive"
                                                                : "secondary"
                                                    }
                                                >
                                                    {status}
                                                </Badge>
                                            </div>
                                        )}
                                    </div>
                                </TabsContent>

                                <TabsContent value="fetch" className="space-y-6">
                                    <div className="text-center mb-6">
                                        <div className="mx-auto w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mb-4">
                                            <Search className="w-8 h-8 text-accent" />
                                        </div>
                                        <h3 className="text-lg font-semibold text-card-foreground mb-2">Retrieve Processed Data</h3>
                                        <p className="text-sm text-muted-foreground">Access previously processed documents by Job ID</p>
                                    </div>

                                    <div className="space-y-4">
                                        {jobs && jobs.length === 0 && (
                                            <Button
                                                onClick={fetchJobs}
                                                variant="outline"
                                                className="w-full border-accent text-accent hover:bg-accent hover:text-accent-foreground bg-transparent dark:hover:bg-accent"
                                            >
                                                <Database className="w-4 h-4 mr-2" />
                                                Load Available Job IDs
                                            </Button>
                                        )}
                                        <div>
                                            <Label htmlFor="job-id-input" className="text-sm font-medium text-card-foreground">
                                                Job ID
                                            </Label>
                                            <select
                                                id="job-id-input"
                                                className="mt-2 w-full border-2 border-border rounded-md p-3 bg-input text-foreground focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                                                value={jobID || ""}
                                                onChange={(e) => setJobID(e.target.value)}
                                            >
                                                <option value="">Select a Job ID</option>
                                                {(jobs ?? []).map((job) => (
                                                    <option key={job.job_id} value={job.job_id}>
                                                        {job.job_id}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                        <Button
                                            onClick={() => jobID && getData(jobID)}
                                            className="w-full h-12 bg-accent hover:bg-accent/90 text-accent-foreground font-medium"
                                            disabled={!jobID || fetching}
                                        >
                                            {fetching ? (
                                                <>
                                                    <div className="w-4 h-4 border-2 border-accent-foreground/30 border-t-accent-foreground rounded-full animate-spin mr-2" />
                                                    Retrieving Data...
                                                </>
                                            ) : (
                                                <>
                                                    <Search className="w-4 h-4 mr-2" />
                                                    Retrieve Document Data
                                                </>
                                            )}
                                        </Button>

                                        {fetchStatus && (
                                            <div className="text-center">
                                                <Badge variant={fetchStatus.includes("Successfully") ? "default" : "secondary"}>
                                                    {fetchStatus}
                                                </Badge>
                                            </div>
                                        )}
                                    </div>
                                </TabsContent>
                            </Tabs>
                        </CardContent>
                    </Card>
                )}

                {jobID && !result && (
                    <Card className="w-full max-w-lg mx-auto shadow-lg border-0 bg-card/80 backdrop-blur-sm">
                        <CardContent className="pt-8 pb-8">
                            <div className="text-center space-y-6">
                                <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                                    <FileText className="w-8 h-8 text-primary" />
                                </div>
                                <div className="space-y-2">
                                    <h2 className="text-xl font-semibold text-card-foreground">Processing Complete</h2>
                                    <p className="text-sm text-muted-foreground">Document successfully processed</p>
                                    <Badge variant="outline" className="text-xs font-mono">
                                        Job ID: {jobID}
                                    </Badge>
                                </div>
                                <Button
                                    onClick={() => getData(jobID)}
                                    disabled={fetching}
                                    className="bg-primary hover:bg-primary/90 text-primary-foreground"
                                >
                                    {fetching ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin mr-2" />
                                            Loading...
                                        </>
                                    ) : (
                                        <>
                                            <FileText className="w-4 h-4 mr-2" />
                                            View Extracted Data
                                        </>
                                    )}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {result && editableData && (
                    <Card className="w-full shadow-lg border-0 bg-card/80 backdrop-blur-sm">
                        <CardHeader className="flex flex-row items-center justify-between border-b border-border/50 pb-4">
                            <div className="space-y-1">
                                <CardTitle className="text-2xl font-semibold text-card-foreground flex items-center gap-2">
                                    <FileText className="w-6 h-6 text-primary" />
                                    Agreement Data
                                </CardTitle>
                                <p className="text-sm text-muted-foreground">
                                    • File Name: {result.filename} <br />• Job ID: {result.job_id}
                                </p>
                            </div>
                            <div className="flex gap-3">
                                {isEditing ? (
                                    <>
                                        <Button
                                            onClick={handleSave}
                                            size="sm"
                                            className="bg-primary hover:bg-primary/90 text-primary-foreground"
                                        >
                                            <Save className="w-4 h-4 mr-2" />
                                            Save Changes
                                        </Button>
                                        <Button onClick={handleEditToggle} variant="outline" size="sm">
                                            Cancel
                                        </Button>
                                    </>
                                ) : (
                                    <>
                                        <Button
                                            onClick={handleEditToggle}
                                            variant="outline"
                                            size="sm"
                                            className="border-primary text-primary hover:bg-primary hover:text-primary-foreground bg-transparent"
                                        >
                                            Edit Data
                                        </Button>
                                        <Button
                                            onClick={() => {
                                                setJobID(null)
                                                setResult(null)
                                                setEditableData(null)
                                                setIsEditing(false)
                                            }}
                                            variant="destructive"
                                            size="sm"
                                            className="ml-2"
                                        >
                                            Restart
                                        </Button>
                                    </>
                                )}
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-8 pt-6">
                            {Object.entries(editableData).map(([sectionKey, sectionValue]) => (
                                <div key={sectionKey} className="space-y-4">
                                    <div className="flex items-center gap-2 pb-2 border-b border-border/30">
                                        <h3 className="text-lg font-semibold capitalize text-card-foreground">
                                            {sectionKey.replace(/_/g, " ")}
                                        </h3>
                                        <Badge variant="secondary" className="text-xs">
                                            {typeof sectionValue === "object" && sectionValue !== null
                                                ? Array.isArray(sectionValue)
                                                    ? `${sectionValue.length} items`
                                                    : `${Object.keys(sectionValue).length} fields`
                                                : "1 field"}
                                        </Badge>
                                    </div>

                                    {typeof sectionValue === "object" && sectionValue !== null ? (
                                        Array.isArray(sectionValue) ? (
                                            <div className="grid gap-4">
                                                {sectionValue.map((item, idx) => (
                                                    <Card key={idx} className="bg-muted/30 border border-border/50">
                                                        <CardContent className="p-4 space-y-3">
                                                            {Object.entries(item).map(([fieldKey, fieldValue]) => (
                                                                <div key={fieldKey} className="space-y-2">
                                                                    <Label className="text-sm font-medium capitalize text-card-foreground">
                                                                        {fieldKey.replace(/_/g, " ")}
                                                                    </Label>
                                                                    {isEditing ? (
                                                                        typeof fieldValue === "string" ? (
                                                                            <Input
                                                                                value={fieldValue}
                                                                                onChange={(e) => {
                                                                                    const updatedArr = [...sectionValue]
                                                                                    updatedArr[idx] = { ...updatedArr[idx], [fieldKey]: e.target.value }
                                                                                    setEditableData({ ...editableData, [sectionKey]: updatedArr })
                                                                                }}
                                                                                className="bg-input border-border focus:border-primary"
                                                                            />
                                                                        ) : (
                                                                            <Textarea
                                                                                value={JSON.stringify(fieldValue, null, 2)}
                                                                                onChange={(e) => {
                                                                                    const updatedArr = [...sectionValue]
                                                                                    updatedArr[idx] = { ...updatedArr[idx], [fieldKey]: e.target.value }
                                                                                    setEditableData({ ...editableData, [sectionKey]: updatedArr })
                                                                                }}
                                                                                className="bg-input border-border focus:border-primary font-mono text-sm"
                                                                                rows={3}
                                                                            />
                                                                        )
                                                                    ) : (
                                                                        <div className="p-3 bg-background rounded-md border border-border/50">
                                                                            <p className="text-sm text-foreground">
                                                                                {typeof fieldValue === "object"
                                                                                    ? JSON.stringify(fieldValue, null, 2)
                                                                                    : String(fieldValue)}
                                                                            </p>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            ))}
                                                        </CardContent>
                                                    </Card>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="grid gap-4 md:grid-cols-2">
                                                {Object.entries(sectionValue).map(([fieldKey, fieldValue]) => (
                                                    <div key={fieldKey} className="space-y-2">
                                                        <Label className="text-sm font-medium capitalize text-card-foreground">
                                                            {fieldKey.replace(/_/g, " ")}
                                                        </Label>
                                                        {isEditing ? (
                                                            typeof fieldValue === "object" && fieldValue !== null && "value" in fieldValue ? (
                                                                <Input
                                                                    value={fieldValue.value ?? ""}
                                                                    onChange={(e) => {
                                                                        setEditableData({
                                                                            ...editableData,
                                                                            [sectionKey]: {
                                                                                ...sectionValue,
                                                                                [fieldKey]: {
                                                                                    ...fieldValue,
                                                                                    value: e.target.value,
                                                                                },
                                                                            },
                                                                        })
                                                                    }}
                                                                    className="bg-input border-border focus:border-primary"
                                                                />
                                                            ) : (
                                                                <Textarea
                                                                    value={
                                                                        typeof fieldValue === "object"
                                                                            ? JSON.stringify(fieldValue, null, 2)
                                                                            : String(fieldValue)
                                                                    }
                                                                    onChange={(e) => {
                                                                        setEditableData({
                                                                            ...editableData,
                                                                            [sectionKey]: {
                                                                                ...sectionValue,
                                                                                [fieldKey]: e.target.value,
                                                                            },
                                                                        })
                                                                    }}
                                                                    className="bg-input border-border focus:border-primary font-mono text-sm"
                                                                    rows={3}
                                                                />
                                                            )
                                                        ) : (
                                                            <div className="p-3 bg-background rounded-md border border-border/50">
                                                                <p className="text-sm text-foreground">
                                                                    {typeof fieldValue === "object"
                                                                        ? "value" in fieldValue
                                                                            ? fieldValue.value || "No data"
                                                                            : JSON.stringify(fieldValue, null, 2)
                                                                        : String(fieldValue)}
                                                                </p>
                                                                {typeof fieldValue === "object" &&
                                                                    fieldValue !== null &&
                                                                    "page_number" in fieldValue && (
                                                                        <Badge variant="outline" className="mt-2 text-xs">
                                                                            Page {fieldValue.page_number}
                                                                        </Badge>
                                                                    )}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        )
                                    ) : (
                                        <div className="p-3 bg-background rounded-md border border-border/50">
                                            <p className="text-sm text-foreground">{String(sectionValue)}</p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    )
}
