import React from "react";
import { Button } from "./ui/button";

export function DownloadLogsButton() {
  const downloadLogs = async () => {
    try {
      const response = await fetch("/logs");
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const blob = await response.blob(); // Convert response to blob
      const url = window.URL.createObjectURL(blob); // Create a blob URL
      const link = document.createElement("a"); // Create an anchor element
      link.href = url;
      link.setAttribute("download", "interactions.log"); // Set download attribute
      document.body.appendChild(link); // Append to the DOM
      link.click(); // Trigger download
      link.remove(); // Clean up
    } catch (error) {
      console.error("Failed to download logs:", error);
      alert("Failed to download logs. Please try again.");
    }
  };

  return (
    <Button
      className="mt-4 p-2 w-full rounded-xl border dark:border-zinc-600"
      onClick={downloadLogs}
    >
      Download Logs
    </Button>
  );
}
