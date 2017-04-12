
&nbsp;

# Bulk REST API

**The Authentication Token must be sent as the "x-authorization" HTTP Header.**

**This API uses a "Live" API key.**

Please see [Accepted CSV Fields](#acceptedfields) for a description of the columns that are accepted in the CSV file being uploaded.

The more data fields included, the better the records can be analyzed.

## Important Information:

If the "export_type" is "single" the results are not 'segmented' in the same manner "multi". It is up to the implementor to examine the results.csv and handle the data accordingly (including separating out any blacklisted entries).

It is recommend to only contact subscribers with the following properties:

1. subscriber_score_bucket of 'high'
2. subscriber_email_status of 'verified'
3. No blacklist hits (examine the following fields: subscriber_email_is_blacklisted, subscriber_email_domain_is_blacklisted, subscriber_signup_domain_is_blacklisted, subscriber_signup_ip_is_blacklisted)

## File Format:

Any file being uploaded must be a correctly formatted Comma Separated Value file (CSV) using *UTF-8 encoding*. See [RFC 4180](http://tools.ietf.org/html/rfc4180). At a minimum, Email is required. We suggest including CAN-SPAM required fields and the API Key can be configured to enforce those requirements. For a list of allowed fields and their descriptions see [Accepted CSV Fields](#acceptedfields).

We have a desktop application available for formatting CSV files available (contact your account manager).

1. The file *must* have a valid header row to indicate which fields are in which columns. See the table of Accepted Fields for a list of acceptable values.
2. Columns must be separated by commas ","
3. All rows must be terminated using Windows line endings (CRLF \\r\\n)
4. All rows must have same number of columns
5. Values containing commas must be quoted with double-quotes (")

    e.g.

    Before: 123 test way, apt #4

    After: "123 test way, apt #4"
6. Values containing double quotes must be quoted with double-quotes (") and the double-quotes within the value must be escaped with a double-quote

    e.g.

    Before: test"one

    After: "test""one"
7. Do not send the string "NULL" if you do not have a value for a field. Just send an empty value.
8. Be careful with time stamps and dates. If you're storing your time stamps and dates as a unix time integer, make sure to *not* send 1970-01-01 00:00:00. Just send an empty value


## Endpoints:

**IMPORTANT** The API Endpoint when viewing the Auth details of the API Key will end in 'verify'. This *must* be changed to 'bulk'

GET to /api/live/bulk (List jobs)

POST to /api/live/bulk (Create Job)

GET to /api/live/bulk/ID (Job Status)

DELETE to /api/live/bulk/ID (Delete job files)

GET to /api/live/bulk/ID/download (Download Job Results)

### Errors:

Any error, no matter the HTTP code, should return a JSON object in the form:
```javascript
        {
            "status": "error",
            "error" : "CODE",
            "msg" : "HUMAN_READABLE_MESSAGE"
        }
```


## List all Jobs [200]:
  No Jobs:
```javascript
    {
        "data":[],
        "total":0
    }
```
  With Jobs:
```javascript
    {
        "data":[
            {
                "download_url":"http://host:port/api/live/bulk/ID/download",
                "job":"ID1",
                "added":"2014-09-19 17:17:46 UTC",
                "started":"2014-09-19 17:18:30 UTC",
                "ended":"2014-09-19 17:19:05 UTC",
                "status":"completed"
            },
            {
                "job":"ID2",
                "added":"2014-09-19 17:17:43 UTC",
                "started":"2014-09-19 17:17:44 UTC",
                "status":"active"
            },
            {
                "job":"ID3",
                "added":"2014-09-19 17:17:44 UTC",
                "status":"pending"
            }
        ],
        "total":3
    }
```
>  Possible job statuses:
>
>  * active
>  * cancelled
>  * completed
>  * paused
>  * pending


## Create a new job:

Creating a job is done as a multipart form POST (encoding multipart/form-data).

Parts of the POST operation:

1. **export_type:** this can be "multi" or "single" (defaults to "multi"). This setting determines how the results are segmented, with "multi" outputing 'high', 'medium', 'low', 'bad' and 'blacklisted' CSVs, and "single" outputting just 'results.csv'.
2. **notify_email:** An email address which will be notified when the job is completed (optional)
3. **max_verify_hours:** The number of hours after which the verification process will be stopped (optional). **When this happens, unverified records will be included in the bad.csv file with a 'notverified' email_status.**
4. the file, which must be of type "text/csv" (required)
5. The **"x-authorization" HTTP header** must be set for all operations. The value of this field is the API Key Authentication Token


### Responses

Success Response [202] (when file is < 500k lines):
```javascript
      {
        "status":"success",
        "jobs":[
          {
            "name":"ID",
            "msg":"FILENAME being processed as a single jobs",
            "status_url":"http://host:port/api/live/bulk/ID"
          }
        ]
      }
```
    Success Response [202] (when file is > 500k lines)
        The system will split the file into multiple jobs)  
        When a file is > 500k lines, the system will automatically split it into
        multiple jobs and append a counter to the job name.
        The counter will take the form of '_00', incrementing from 00 to 99.
```javascript
      {
        "status":"success",
        "jobs":[
          {
            "name":"ID",
            "msg":"FILENAME being processed as a multiple jobs",
            "status_url":"http://host:port/api/live/bulk/ID"
          },
          {
            "name":"ID2",
            "msg":"FILENAME being processed as a multiple jobs",
            "status_url":"http://host:port/api/live/bulk/ID2"
          }
        ]
      }
```
    Failure Response [400]:
```javascript
      {
        "status":"error",
        "error":"bad_parameter",
        "msg":"Missing CSV file in POST"
      }
```
An error should always contain 'status' as 'error', the 'error' code and a readable message in 'msg'

>  Possible error codes:
>
>  * not_found
>  * bad_parameter
>  * already_deleted
>  * missing
>  * out_of_credits


## Get the status of a Job:
  Failure [404] if the job is not found:
```javascript
    {
      "status" : "error",
      "error" : "not_found",
      "msg" : "Cannot find job ID"
    }
```
  Success [200]:
```javascript
    {
      "job":"ID",
      "added":"2014-09-19 17:49:20 UTC",
      "started":"2014-09-19 17:49:21 UTC",
      "status":"active"
    }
```
    **and when it's completed**
```javascript
    {
      "download_url":"http://host:port/api/live/bulk/ID/download",
      "job":"ID",
      "added":"2014-09-19 17:49:20 UTC",
      "started":"2014-09-19 17:49:21 UTC",
      "ended":"2014-09-19 17:49:57 UTC",
      "status":"completed"
    }
```

## Delete the source and results files for a job once you've downloaded successfully:
  Failure [404] if the job is not found
```javascript
    {
      "status" : "error",
      "error" : "not_found",
      "msg" : "Cannot find job ID"
    }
```
  Failure [400] if the job cannot be deleted
```javascript
    {
      "status" : "error",
      "error" : "Not_completed",
      "msg" : "Only completed jobs can have files deleted"
    }
```
  Success [200]
```javascript
    {
      "status" : "deleted",
      "msg" : "All files for job \"ID\" have been deleted"
    }
```

## Download the results **when the job is completed**:
  Failure [404] - Job not found
```javascript
    {
      "status" : "error",
      "error" : "not_found",
      "msg" : "Cannot find job results file for ID"
    }
```
  Failure [404] - Job already deleted
```javascript
    {
      "status" : "error",
      "error" : "already_deleted",
      "msg" : "Files for ID already deleted"
    }
```
  Failure [404] - Not ready for download
```javascript
    {
      "status" : "error",
      "error" : "not_ready",
      "msg" : "File is not available for download until the job has completed"
    }
```
  Failure [409] - Requesting wrong data
```javascript
    {
      "status" : "error",
      "error" : "conflict",
      "msg" : "File not available for this job type"
    }
```

## Download the results **when the job is not yet completed**:
  Returns status [200]
```javascript
    {
      "status" : "X",
      "msg" : "Job \"ID\" is currently \"X\""
    }
```
    Where X is 'pending', 'paused', 'active', 'completed', 'cancelled'



---------------------------------------------------------


## Accepted CSV Fields: {#acceptedfields}

The CSV must contain a header row which consists of field names matching those listed below.

Field | Description
:-----|:----------
subscriber_email | Email Address **required**
subscriber_fname | First Name **suggested**
subscriber_mname | Middle Name or Initial(s)
subscriber_lname | Last Name **suggested**
subscriber_addr1 | Address Line 1
subscriber_addr2 | Address Line 2
subscriber_phone | Phone Number
subscriber_mobile | Mobile Phone Number
subscriber_fax | Fax Number
subscriber_city | City **suggested**
subscriber_state | State/Region Code **suggested**
subscriber_zip | Zip/Postal Code **suggested**
subscriber_country | Country Code (2 character) **suggested**
subscriber_gender | Gender (M/F) **suggested**
subscriber_dob | Date of Birth. "YYYY-MM-DD" format **suggested**
subscriber_signup_ip | Sign up IP Address **suggested**
subscriber_signup_tstamp | Sign up Time stamp "YYYY-MM-DD hh:ii:ssZ" Format **suggested**
subscriber_signup_url | Sign up Web page URL **suggested**
subscriber_signup_category | Sign up Web page Category (See <b>Categories</b> below) **suggested**
subscriber_last_activity_tstamp | Time stamp of when subscriber last interacted. "YYYY-MM-DD hh:ii:ssZ" Format
subscriber_reference | Used for matching records between systems
custom_ | Any header starting with "custom_" \*

\* Custom Headers:  will be passed through from the input file into the results file in the correct position


## Categories

<table border=1>
      <tbody>
        <tr>
          <td>Automotive</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;Automotive::Maintenance</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp;   Automotive::Parts
            </td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Automotive::Sales</td>
        </tr>
        <tr>
          <td>Bizop</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Bizop::Make Money From Home</td>
        </tr>
        <tr>
          <td>Business Services</td>
        </tr>
        <tr>
          <td>Careers &amp; Employment</td>
        </tr>
        <tr>
          <td>Computers &amp; Communications</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Cable Bundle</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Cable TV</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Cellular/Mobile Packages</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Cellular/Mobile Phones</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Computer Hardware</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Computer Software</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Consulting Services</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Internet Services</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Satellite TV</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::Video Games</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Computers &amp; Communications::VOIP</td>
        </tr>
        <tr>
          <td>Consumer Packaged Goods</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Consumer Packaged Goods::Food products</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Consumer Packaged Goods::Household products</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Consumer Packaged Goods::Packaged goods</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Consumer Packaged Goods::Tobacco</td>
        </tr>
        <tr>
          <td>Dating</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Dating::Adult Dating</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Dating::Christian Dating</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Dating::International Dating</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Dating::Senior Dating</td>
        </tr>
        <tr>
          <td>Education</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Education::Accounting Program</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Education::Art &amp; Design Program</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Education::Business Program</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Education::Education Program</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Education::Health Science Program</td>
        </tr>
        <tr>
          <td class="double-indent">
            Education::Health Science Program::Dental Assistant Degree</td>
        </tr>
        <tr>
          <td class="double-indent">
            Education::Health Science Program::Medical Admin Degree</td>
        </tr>
        <tr>
          <td class="double-indent">
            Education::Health Science Program::Nursing Degree</td>
        </tr>
        <tr>
          <td class="double-indent">
            Education::Health Science Program::Pharmacy Assistant Degree</td>
        </tr>
        <tr>
          <td class="double-indent">
            Education::Health Science Program::Ultrasound Tech Degree</td>
        </tr>
        <tr>
          <td class="double-indent">
            Education::Health Science Program::X-ray Tech Degree</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp;   Education::High School Diploma
            </td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp;   Education::Legal Program
            </td>
        </tr>
        <tr>
          <td class="double-indent">
            Education::Legal Program::Criminal Justice Degree</td>
        </tr>
        <tr>
          <td class="double-indent">
            Education::Legal Program::Paralegal Degree</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Education::Online Degree</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Education::Technology Program</td>
        </tr>
        <tr>
          <td>Entertainment</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Entertainment::Amusement</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Entertainment::Box Office</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Entertainment::Film</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Entertainment::Music</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Entertainment::Recreation</td>
        </tr>
        <tr>
          <td>Events</td>
        </tr>
        <tr>
          <td>Family</td>
        </tr>
        <tr>
          <td>Financial</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Auto Loans</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Business credit institutions</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Commercial banks</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Consumer finance companies</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Credit agencies</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Credit Card</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Credit card agencies</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Credit Repair</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Debt Consolidation</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Grants</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Grants::Education Grant</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Grants::Government Grant</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Loan companies</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Payday Loans</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Personal credit</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Personal Loan</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Refinance</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Securities</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Student Loan</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Taxes</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::Underwriting</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Financial::VA Loans</td>
        </tr>
        <tr>
          <td>Fundraisers</td>
        </tr>
        <tr>
          <td>Health &amp; Beauty</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Health &amp; Beauty::Anti-aging</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Health &amp; Beauty::Cosmetics</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Health &amp; Beauty::Diet &amp; Weight Loss</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Health &amp; Beauty::Fitness</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Health &amp; Beauty::Medical Services</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Health &amp; Beauty::Pharmaceuticals</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Health &amp; Beauty::Skin Care</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Health &amp; Beauty::Toiletries</td>
        </tr>
        <tr>
          <td>Insurance</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Insurance::Auto Insurance</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Insurance::Dental Insurance</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Insurance::Health Insurance</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Insurance::Home Insurance</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Insurance::Life Insurance</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Insurance::travel Insurance</td>
        </tr>
        <tr>
          <td>Legal Services</td>
        </tr>
        <tr>
          <td>Leisure &amp; travel</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Leisure &amp; travel::Airline</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Leisure &amp; travel::Hotel</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Leisure &amp; travel::Resort</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Leisure &amp; travel::travel</td>
        </tr>
        <tr>
          <td>Media</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Media::Books</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Media::Magazines</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Media::Newspapers</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Media::Radio</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Media::TV</td>
        </tr>
        <tr>
          <td>Newsletters</td>
        </tr>
        <tr>
          <td>Pets</td>
        </tr>
        <tr>
          <td>Pharma &amp; Healthcare</td>
        </tr>
        <tr>
          <td>Promotional Offer</td>
        </tr>
        <tr>
          <td>Real Estate</td>
        </tr>
        <tr>
          <td>Retail</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Apparel</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Appliances</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Coupons</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Drugstores</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Fast food</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Home furnishings</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Home &amp; Garden</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Jewelry</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Mail order/catalog</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Pet food/supplies</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Restaurants</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Retail stores</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Textiles</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Retail::Toys</td>
        </tr>
        <tr>
          <td>Telecommunications</td>
        </tr>
        <tr>
          <td>Warranty</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Warranty::Auto Warranty</td>
        </tr>
        <tr>
          <td>&nbsp;&nbsp;&nbsp;&nbsp; Warranty::Home Warranty</td>
        </tr>
      </tbody><tbody>
    </tbody></table>
