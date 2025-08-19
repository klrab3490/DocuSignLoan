"use client";

import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Trash2, Plus, Save, Upload, FileText, Search } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type Party = {
    name: string
    role: string
}

type Clause = {
    type: "Article" | "Schedule"
    article?: string
    title: string
}

type ExtractedResult = {
    agreement_name: string
    agreement_date: string
    parties: Party[]
    clauses: Clause[]
}

type JobResult = {
    job_id: string
    status: string
    filename: string
    result: ExtractedResult
}

export default function Home() {
    const [file, setFile] = useState<File | null>(null)
    const [status, setStatus] = useState<string | null>(null)
    const [fetching, setFetching] = useState<boolean>(false)
    const [jobID, setJobID] = useState<string | null>(null)
    const [result, setResult] = useState<JobResult | null>(null)
    const [editableData, setEditableData] = useState<ExtractedResult | null>(null)
    const [isEditing, setIsEditing] = useState(false)
    const [jobs, setJobs] = useState<string[]>([])
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
            // console.log("Fetched jobs:", data);
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
        const result = await fetch(`http://localhost:8000/pdf/status/${id}/`)
        if (!result.ok) throw new Error("Failed to fetch data")
        const data = await result.json()

        // pick first page’s extracted_data or merge pages
        const firstPage = data.result?.[0]?.extracted_data || {}

        const formattedResult: JobResult = {
            job_id: id,
            status: data.status,
            filename: data.filename || "",
            result: {
                agreement_name: firstPage.general?.document_type || "",
                agreement_date: firstPage.dates?.agreement_date || "",
                parties: [
                    { name: firstPage.general?.parties?.construction_receiver || "", role: "Construction Receiver" },
                    { name: firstPage.general?.parties?.administrative_agent || "", role: "Administrative Agent" },
                    { name: firstPage.general?.parties?.lenders || "", role: "Lender(s)" }
                ],
                clauses: (firstPage.general?.table_of_contents_articles || []).map((a: string) => ({
                    type: "Article",
                    article: a.split(" ")[1] || "",
                    title: a
                }))
            }
        }

        setResult(formattedResult)
        setEditableData(formattedResult.result)
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

    const addParty = () => {
        if (editableData) {
            setEditableData({
                ...editableData,
                parties: [...editableData.parties, { name: "", role: "" }],
            })
        }
    }

    const removeParty = (index: number) => {
        if (editableData) {
            setEditableData({
                ...editableData,
                parties: editableData.parties.filter((_, i) => i !== index),
            })
        }
    }

    const updateParty = (index: number, field: keyof Party, value: string) => {
        if (editableData) {
            const updatedParties = editableData.parties.map((party, i) =>
                i === index ? { ...party, [field]: value } : party,
            )
            setEditableData({ ...editableData, parties: updatedParties })
        }
    }

    const addClause = () => {
        if (editableData) {
            setEditableData({
                ...editableData,
                clauses: [...editableData.clauses, { type: "Article", article: "", title: "" }],
            })
        }
    }

    const removeClause = (index: number) => {
        if (editableData) {
            setEditableData({
                ...editableData,
                clauses: editableData.clauses.filter((_, i) => i !== index),
            })
        }
    }

    const updateClause = (index: number, field: keyof Clause, value: string) => {
        if (editableData) {
            const updatedClauses = editableData.clauses.map((clause, i) =>
                i === index ? { ...clause, [field]: value } : clause,
            )
            setEditableData({ ...editableData, clauses: updatedClauses })
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6">
            <div className="max-w-4xl mx-auto space-y-6">
                {!jobID && !result && (
                    <Card className="w-full max-w-lg mx-auto">
                        <CardHeader className="text-center">
                            <CardTitle className="text-2xl font-bold text-slate-800 dark:text-slate-200">PDF Processing</CardTitle>
                            <p className="text-slate-600 dark:text-slate-400">Upload a new PDF or fetch existing data by Job ID</p>
                        </CardHeader>
                        <CardContent>
                            <Tabs defaultValue="upload" className="w-full">
                                <TabsList className="grid w-full grid-cols-2">
                                    <TabsTrigger value="upload" className="flex items-center gap-2">
                                        <Upload className="w-4 h-4" />
                                        Upload PDF
                                    </TabsTrigger>
                                    <TabsTrigger value="fetch" className="flex items-center gap-2">
                                        <Search className="w-4 h-4" />
                                        Fetch by ID
                                    </TabsTrigger>
                                </TabsList>

                                <TabsContent value="upload" className="space-y-4 mt-4">
                                    <div className="text-center mb-4">
                                        <div className="mx-auto w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                                            <Upload className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                        </div>
                                    </div>
                                    <div>
                                        <Label htmlFor="pdf-upload" className="text-sm font-medium">PDF Document</Label>
                                        <Input id="pdf-upload" type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mt-1" />
                                    </div>
                                    <Button
                                        onClick={(e) => {
                                            e.preventDefault()
                                            handleUpload()
                                        }}
                                        className="w-full"
                                        disabled={!file || status === "Uploading"}
                                    >
                                        {status === "Uploading" ? "Uploading..." : "Upload PDF"}
                                    </Button>
                                    {status && <p className="text-sm text-center text-slate-600 dark:text-slate-400">{status}</p>}
                                </TabsContent>

                                <TabsContent value="fetch" className="space-y-4 mt-4">
                                    <div className="text-center mb-4">
                                        <div className="mx-auto w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                                            <Search className="w-6 h-6 text-green-600 dark:text-green-400" />
                                        </div>
                                    </div>
                                    {jobs.length == 0 && (
                                        <Button onClick={fetchJobs}>Fetch All job IDs</Button>
                                    )}
                                    <div>
                                        <Label htmlFor="job-id-input" className="text-sm font-medium">Job ID</Label>
                                        <select
                                            id="job-id-input"
                                            className="mt-1 w-full border rounded p-2 bg-white dark:bg-slate-900"
                                            value={jobID || ""}
                                            onChange={(e) => setJobID(e.target.value)}
                                        >
                                            <option value="">Select Job ID</option>
                                            {jobs.map((id) => (
                                                <option key={id} value={id}>
                                                    {id}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <Button
                                        onClick={() => jobID && getData(jobID)}
                                        className="w-full mt-2"
                                        disabled={!jobID || fetching}
                                    >
                                        {fetching ? "Fetching..." : "Fetch Data"}
                                    </Button>

                                    {fetchStatus && (
                                        <p className="text-sm text-center text-slate-600 dark:text-slate-400">{fetchStatus}</p>
                                    )}
                                </TabsContent>
                            </Tabs>
                        </CardContent>
                    </Card>
                )}

                {jobID && !result && (
                    <Card className="w-full max-w-lg mx-auto">
                        <CardContent className="pt-6">
                            <div className="text-center space-y-4">
                                <div className="mx-auto w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                                    <FileText className="w-6 h-6 text-green-600 dark:text-green-400" />
                                </div>
                                <div>
                                    <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200">Processing Complete</h2>
                                    <p className="text-sm text-slate-600 dark:text-slate-400">Job ID: {jobID}</p>
                                </div>
                                <Button onClick={() => getData(jobID)} disabled={fetching}>
                                    {fetching ? "Loading..." : "View Extracted Data"}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {result && editableData && (
                    <Card className="w-full">
                        <CardHeader className="flex flex-row items-center justify-between">
                            <CardTitle className="text-xl font-bold text-slate-800 dark:text-slate-200">Agreement Data</CardTitle>
                            <div className="flex gap-2">
                                {isEditing ? (
                                    <>
                                        <Button onClick={handleSave} size="sm">
                                            <Save className="w-4 h-4 mr-2" />
                                            Save Changes
                                        </Button>
                                        <Button onClick={handleEditToggle} variant="outline" size="sm">
                                            Cancel
                                        </Button>
                                    </>
                                ) : (
                                    <Button onClick={handleEditToggle} variant="outline" size="sm">
                                        Edit Data
                                    </Button>
                                )}
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Agreement Basic Info */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <Label htmlFor="agreement-name">Agreement Name</Label>
                                    {isEditing ? (
                                        <Input
                                            id="agreement-name"
                                            value={editableData.agreement_name}
                                            onChange={(e) =>
                                                setEditableData({
                                                    ...editableData,
                                                    agreement_name: e.target.value,
                                                })
                                            }
                                            className="mt-1"
                                        />
                                    ) : (
                                        <p className="mt-1 p-2 bg-slate-50 dark:bg-slate-800 rounded border">
                                            {editableData.agreement_name}
                                        </p>
                                    )}
                                </div>
                                <div>
                                    <Label htmlFor="agreement-date">Agreement Date</Label>
                                    {isEditing ? (
                                        <Input
                                            id="agreement-date"
                                            value={editableData.agreement_date}
                                            onChange={(e) =>
                                                setEditableData({
                                                    ...editableData,
                                                    agreement_date: e.target.value,
                                                })
                                            }
                                            className="mt-1"
                                        />
                                    ) : (
                                        <p className="mt-1 p-2 bg-slate-50 dark:bg-slate-800 rounded border">
                                            {editableData.agreement_date}
                                        </p>
                                    )}
                                </div>
                            </div>

                            {/* Parties Section */}
                            <div>
                                <div className="flex items-center justify-between mb-3">
                                    <Label className="text-base font-semibold">Parties</Label>
                                    {isEditing && (
                                        <Button onClick={addParty} size="sm" variant="outline">
                                            <Plus className="w-4 h-4 mr-2" />
                                            Add Party
                                        </Button>
                                    )}
                                </div>
                                <div className="space-y-3">
                                    {(Array.isArray(editableData.parties) ? editableData.parties : []).map((party, index) => (
                                        <div key={index} className="flex gap-3 items-end">
                                            <div className="flex-1">
                                                <Label htmlFor={`party-name-${index}`}>Name</Label>
                                                {isEditing ? (
                                                    <Input
                                                        id={`party-name-${index}`}
                                                        value={party.name}
                                                        onChange={(e) => updateParty(index, "name", e.target.value)}
                                                        className="mt-1"
                                                    />
                                                ) : (
                                                    <p className="mt-1 p-2 bg-slate-50 dark:bg-slate-800 rounded border">{party.name}</p>
                                                )}
                                            </div>
                                            <div className="flex-1">
                                                <Label htmlFor={`party-role-${index}`}>Role</Label>
                                                {isEditing ? (
                                                    <Input
                                                        id={`party-role-${index}`}
                                                        value={party.role}
                                                        onChange={(e) => updateParty(index, "role", e.target.value)}
                                                        className="mt-1"
                                                    />
                                                ) : (
                                                    <Badge variant="secondary" className="mt-1 block w-fit">
                                                        {party.role}
                                                    </Badge>
                                                )}
                                            </div>
                                            {isEditing && (
                                                <Button onClick={() => removeParty(index)} size="sm" variant="destructive">
                                                    <Trash2 className="w-4 h-4" />
                                                </Button>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Clauses Section */}
                            <div>
                                <div className="flex items-center justify-between mb-3">
                                    <Label className="text-base font-semibold">Clauses</Label>
                                    {isEditing && (
                                        <Button onClick={addClause} size="sm" variant="outline">
                                            <Plus className="w-4 h-4 mr-2" />
                                            Add Clause
                                        </Button>
                                    )}
                                </div>
                                <div className="space-y-3">
                                    {(Array.isArray(editableData.clauses) ? editableData.clauses : []).map((clause, index) => (
                                        <div key={index} className="space-y-2 p-3 border rounded-lg">
                                            <div className="flex gap-3 items-end">
                                                <div className="flex-1">
                                                    <Label htmlFor={`clause-article-${index}`}>Article</Label>
                                                    {isEditing ? (
                                                        <Input
                                                            id={`clause-article-${index}`}
                                                            value={clause.article || ""}
                                                            onChange={(e) => updateClause(index, "article", e.target.value)}
                                                            className="mt-1"
                                                        />
                                                    ) : (
                                                        <p className="mt-1 p-2 bg-slate-50 dark:bg-slate-800 rounded border">
                                                            Article {clause.article}
                                                        </p>
                                                    )}
                                                </div>
                                                {isEditing && (
                                                    <Button onClick={() => removeClause(index)} size="sm" variant="destructive">
                                                        <Trash2 className="w-4 h-4" />
                                                    </Button>
                                                )}
                                            </div>
                                            <div>
                                                <Label htmlFor={`clause-title-${index}`}>Title</Label>
                                                {isEditing ? (
                                                    <Textarea
                                                        id={`clause-title-${index}`}
                                                        value={clause.title}
                                                        onChange={(e) => updateClause(index, "title", e.target.value)}
                                                        className="mt-1"
                                                        rows={2}
                                                    />
                                                ) : (
                                                    <p className="mt-1 p-2 bg-slate-50 dark:bg-slate-800 rounded border">{clause.title}</p>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    )
}
