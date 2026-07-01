If the same company uses AWS, Azure, and GCP, why is a unified schema better than storing each provider's billing format separately?
A:- Because today we use cloud and it name says cp and tmrw we can use azure whose name will be ec2. So here there will be disaster in the db. so its better to give it a unified which we will design by ourself

If tomorrow a new cloud provider appears (for example, DigitalOcean), how should our architecture allow us to add it without changing the entire application?
A:-Because we are not taking the names as it is. We are giving the service a unified name according to us which will be the same no matter whichever service we will use so no need to change the entire work