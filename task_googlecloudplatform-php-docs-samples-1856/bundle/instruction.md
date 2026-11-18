## Description

The PHP documentation samples for Google Cloud Data Loss Prevention currently lack an example showing how to de-identify files stored in Cloud Storage. Developers who want to protect sensitive information in their Cloud Storage buckets by running de-identification jobs through the DLP API have no reference sample to start from.

## Expected Behavior

- A new sample file should demonstrate the complete workflow for submitting a Cloud Storage de-identification job via the DLP API.
- The sample should accept configuration for the input Cloud Storage location, the output Cloud Storage location, separate de-identification templates for unstructured files, structured files, and images, and a BigQuery table for storing transformation details.
- Once a job is submitted, the sample should wait for the job to finish and then print a summary including the job name and the types of sensitive information discovered (with their counts).

## Why This Matters

Without a working code example, developers must piece together the correct combination of API calls, job configuration, and polling logic from raw reference documentation. A self-contained, runnable sample significantly reduces the integration effort and serves as a concrete starting point for teams that need to de-identify sensitive data in Cloud Storage at scale.

I'm working with the Google Cloud Data Loss Prevention API in PHP and I need to add a sample that demonstrates how to de-identify sensitive files stored in Cloud Storage. There doesn't seem to be an existing example for this workflow in the PHP samples collection.

The sample should show how to create and submit a de-identification job that reads from one Cloud Storage location and writes the de-identified output to another. It should support configuring separate templates for unstructured files, structured data files, and images, and also allow specifying a BigQuery table where transformation details get stored.

Once the job is submitted, the sample needs to poll until the job completes, then print the job's name and a summary of all the sensitive information types that were found, along with their counts. Could you add this sample to the dlp/src directory?

## Additional Requirements

Your implementation must expose the following public API exactly as named, since downstream callers depend on these exact identifiers/signatures:

- `deidentify_cloud_storage` (function)
