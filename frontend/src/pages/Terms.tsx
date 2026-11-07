import { LegalLayout, LegalSection } from "@/components/legal/LegalLayout";

export function Terms() {
  return (
    <LegalLayout title="Terms of Use" updated="7 November 2026">
      <p className="leading-relaxed text-ink-muted">
        By creating an account or using ResumeIQ you agree to these terms.
        ResumeIQ is a free beta service run by Mujahid Adam.
      </p>

      <LegalSection heading="What the service does">
        <p>
          ResumeIQ uses AI to score resumes, suggest improvements and draft cover
          letters. It is a writing aid, not professional career, legal or
          hiring advice.
        </p>
      </LegalSection>

      <LegalSection heading="AI output can be wrong">
        <p>
          Scores, suggestions and generated text may be inaccurate, incomplete or
          unsuitable for a particular employer. Review everything before you
          send it. You are responsible for what you submit to employers.
        </p>
      </LegalSection>

      <LegalSection heading="Your content">
        <p>
          You keep ownership of the resumes and job descriptions you upload. You
          confirm that you have the right to upload them, and that they contain
          your own information or information you are allowed to share. You
          allow ResumeIQ to process them as described in the Privacy Policy.
        </p>
      </LegalSection>

      <LegalSection heading="Acceptable use">
        <ul className="list-disc space-y-1.5 pl-5">
          <li>Do not upload other people&apos;s personal data without permission.</li>
          <li>Do not try to break, overload or reverse-engineer the service.</li>
          <li>Do not use automated tools to bypass the usage limits.</li>
          <li>Do not use the service for anything unlawful.</li>
        </ul>
        <p>Usage limits apply and may change at any time.</p>
      </LegalSection>

      <LegalSection heading="Availability and changes">
        <p>
          The service is provided as is, without warranties, and may be slow,
          change, be reset or stop at any time during the beta. I may suspend
          accounts that break these terms.
        </p>
      </LegalSection>

      <LegalSection heading="Liability">
        <p>
          To the extent the law allows, I am not liable for losses arising from
          your use of ResumeIQ, including job outcomes or lost data.
        </p>
      </LegalSection>

      <LegalSection heading="Changes to these terms">
        <p>
          I may update these terms. The date above shows the latest version, and
          continuing to use the service means you accept it.
        </p>
      </LegalSection>
    </LegalLayout>
  );
}
