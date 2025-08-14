"use client"

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type Party = {
    name: string;
    role: string;
};

type Clause = {
    type: "Article" | "Schedule";
    article?: string;
    title: string;
};

type ExtractedResult = {
    agreement_name: string;
    agreement_date: string;
    parties: Party[];
    clauses: Clause[];
};

type JobResult = {
    job_id: string;
    status: string;
    filename: string;
    result: ExtractedResult;
};

export default function Home() {
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<string | null>(null);
    const [fetching, setFetching] = useState<boolean>(false);
    const [jobID, setJobID] = useState<string | null>(null);
    const [result, setResult] = useState<JobResult | null>(null);

    const handleUpload = async () => {
        setStatus("Uploading");
        if (!file) {
            setStatus("No file selected");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const result = await fetch("http://localhost:8000/pdf/extract-and-format/", {
                method: "POST",
                body: formData,
            });

            if (!result.ok) {
                setStatus("Upload failed");
                return;
            }

            const data = await result.json();
            setJobID(data.job_id);
            setStatus("Upload successful");
            // console.log(data);
        } catch (error) {
            setStatus("Error uploading");
            console.error(error);
        }
    }

    const getData = async (id: string) => {
        setFetching(true);
        if (!id) return;

        try{
            const result = await fetch(`http://localhost:8000/pdf/status/${id}/`);
            if (!result.ok) throw new Error("Failed to fetch data");
            const data = await result.json();
            setResult(data);
            // console.log(data);
        } catch (error) {
            console.error(error);
        } finally {
            setFetching(false);
        }
    }

    return (
        <div className="font-sans min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 dark:from-gray-900 dark:to-gray-800 flex flex-col items-center justify-center p-6">
            <main className="bg-white dark:bg-gray-900 shadow-xl rounded-xl p-10 flex flex-col gap-8 items-center w-full max-w-lg">
                {!jobID && (
                    <section>
                        <h1 className="text-3xl font-extrabold text-blue-700 dark:text-blue-300 mb-2">Upload Your PDF</h1>
                        <p className="text-gray-600 dark:text-gray-300 mb-6 text-center">
                            Select a PDF file to upload and process your loan documents securely.
                        </p>
                        <form className="flex flex-col gap-4 w-full">
                            <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="pdf-upload">
                                PDF File
                            </label>
                            <Input
                                id="pdf-upload"
                                type="file"
                                accept="application/pdf"
                                onChange={(e) => setFile(e.target.files ? e.target.files?.[0] : null)}
                                className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-700 transition bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                            />
                            <Button
                                onClick={(e) => {
                                    e.preventDefault();
                                    handleUpload();
                                }}
                                type="submit"
                                className="mt-4 px-6 py-2 bg-blue-600 dark:bg-blue-700 text-white font-semibold rounded-lg hover:bg-blue-700 dark:hover:bg-blue-800 transition"
                                disabled={!file || status === "Uploading"}
                            >
                                {status === "Uploading" ? "Uploading..." : "Upload PDF"}
                            </Button>
                        </form>
                    </section>
                )}

                {jobID && !result && (
                    <div className="mt-6">
                        <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">
                            Job ID: {jobID}
                        </h2>
                        <Button onClick={() => getData(jobID)}>
                            {fetching ? "Fetching..." : "Show Data"}
                        </Button>
                    </div>
                )}

                {result && (
                    <div className="mt-6">
                        <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">
                            Extracted Data
                        </h2>
                        <form className="mt-2 flex flex-col gap-4 text-sm text-gray-700 dark:text-gray-200">
                            <div className="flex gap-1">
                                <label className="font-semibold">Agreement Name:</label>
                                <div>{result.result.agreement_name}</div>
                            </div>
                            <div className="flex gap-1">
                                <label className="font-semibold">Agreement Date:</label>
                                <div>{result.result.agreement_date}</div>
                            </div>
                            <div>
                                <label className="font-semibold">Parties:</label>
                                <ul className="list-disc ml-6">
                                    {result.result.parties.map((party, idx) => (
                                        <li key={idx}>
                                            <span className="font-medium">{party.name}</span> ({party.role})
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div>
                                <label className="font-semibold">Clauses:</label>
                                <ul className="list-disc ml-6">
                                    {result.result.clauses.map((clause, idx) => (
                                        <li key={idx}>
                                            <span className="font-medium">Article {clause.article}</span>                                            
                                            : {clause.title}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </form>
                    </div>
                )}
            </main>
        </div>
    );
}
