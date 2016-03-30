#TrackRx Ultrasound

Used to communicate between either a laptop and a TrackRx bottle, or a 
smartphone and a TrackRx bottle. A message is sent using On-Of Keying (OOK),
a form of one bit ASK. It consists of a start byte of 0xFF, followed by a payload, 
and then a stop byte of 0x00. A payload consists of the bits of each character repeated
three time plus a parity bit also repeated three times . So, if 'a' 
('11000001', parity '1') is sent, it is coded as:
'111 111 000 000 000 000 000 111 111'.

Thus, the 
message 'ab' would be

0xFF FC003F FC01C7 00

##Dependencies
pyaudio
