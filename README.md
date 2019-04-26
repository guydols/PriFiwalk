# PriFiwalk
A, privacy first, file system research tool.

Doing research in the field of digital forensics without a budget can be hard. Using volunteers can help gather research data without costs. For compensation of a volunteer's data PriFiwalk upholds their privacy by removal of any potential private data. This ensures that the data meets privacy data regulations like the EU's GDPR and makes volunteer's more likely to join in their data.

PriFiwalk makes use of the sleuthkit and several tools from GNU/linux to gather information on a system, it's storage devices and the files on those storages devices. It's been designed and build to be used in a portable manner for the research (insert paper here) of Vincent van der Meer. The idea that we could use multiple USB flash drives with Linux and boot these on the laptops of volunteer's ensures a couple of benefits:
* The volunteer's computer does not need to install or change to be able to run the PriFiwalk (except for BIOS/UEFI options for booting);
* The volunteer's computer has to be shutdown which means that the operating system can not make changes while PriFiwalk is running;
* The data from PriFiwalk is stored on the USB flash drive which makes it easy to collect from multiple source;
* The data can be processed at a later time (except the scrubbing of private data), this keeps the running time of PriFiwalk lower which makes volunteer's happier;

## Requirements
* GNU/Linux (lsblk, blockdev, udevadm)
* Python 3.7
* sleuthkit (fiwalk)
* xmlstarlet

## Usage
`git clone https://github.com/guydols/PriFiwalk.git`

`cd PriFiwalk`

`python prifiwalk`
