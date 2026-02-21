import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SYNTHIA — Control Tower",
  description: "ARCHONX multi-agent supervision dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          backgroundColor: "#0a0a0f",
          color: "#e0e0e0",
        }}
      >
        {children}
      </body>
    </html>
  );
}
