param(
    [string]$To,
    [string]$Subject,
    [string]$Body
)

$From       = "prekshak014@gmail.com"
$Pass       = "fhlgqvuvtuqxttpq"
$SmtpServer = "smtp.gmail.com"        
$Port       = 587

$Cred = New-Object System.Management.Automation.PSCredential(
    $From,
    (ConvertTo-SecureString $Pass -AsPlainText -Force)
)

Send-MailMessage `
    -To $To `
    -From $From `
    -Subject $Subject `
    -Body $Body `
    -SmtpServer $SmtpServer `
    -Port $Port `
    -UseSsl `
    -Credential $Cred