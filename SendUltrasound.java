public class SendUltrasound
{
	private static int rate = 44100;
	private static int frequency = 19100;
	private static int channels = 1;
	private static int datasize = 441;
	private static String START_STRING = "11111111";
	private static String STOP_STRING = "00000000";

	public static void main(String[] args)
	{
		/* To send a message, generate the pattern and then
		*  generate the tone. The return value of toneGenerator
		*  is what should be played 
		*/
		String pattern = patternGenerator("ab");
		int[] tone = toneGenerator(pattern, frequency, datasize, rate);
	}

	/* Helper method for patternGenerator
	*  input: a message String
	*  ouput: an array of Strings that represent the binary
			  representation of each character in the message
	*/
	private static String[] binaryArrayGenerator(String message)
	{
		byte[] byteMessage = message.getBytes();
		String[] binaryRepArray = new String[byteMessage.length];
		for (int i = 0; i < byteMessage.length; i++)
		{
			byte b = byteMessage[i];
			StringBuilder binaryMessage = new StringBuilder();
			// only care about bits 6-0
			for(int j = 6; j >= 0; j--)
				binaryMessage.append(((b & (1 << j)) != 0) ? 1 : 0);
			binaryRepArray[i] = binaryMessage.toString();
		}
		return binaryRepArray;
	}

	private static String patternGenerator(String message)
	{
		String[] binArray = binaryArrayGenerator("ab");
		String pattern = "";

		for (String character : binArray)
		{
			int parity = 0;
			String stringChar;
			for (int i = 0; i < character.length(); i++)
			{
				stringChar = Character.toString(character.charAt(i));
				pattern += stringChar + stringChar + stringChar;
				parity += (stringChar.equals("1")) ? 1 : 0;
			}
			parity = parity % 2;
			String stringParity = Integer.toString(parity);
			pattern += stringParity + stringParity + stringParity; 
		}
		pattern = START_STRING + pattern + STOP_STRING;
		return pattern;
	}

	private static int[] toneGenerator(String pattern, int freq, int datasize,
										int rate)
	{
		int offset, amp;
		String bit;
		int[] tone = new int[pattern.length()*datasize];
		
		offset = 0;
		for(int i = 0; i < pattern.length(); i++)
		{
			bit = Character.toString(pattern.charAt(i));
			amp = (bit.equals("1")) ? 12000 : 0;
			int[] sine = sineGenerator(freq, datasize, rate, amp, offset);
			for(int j = 0; j < sine.length; j++)
			{
				tone[i*datasize+j] = sine[j];
			}
			offset += datasize;	
		}
		return tone;
	}

	private static int[] sineGenerator(int frequency, int datasize, int rate,
										int amp, int offset)
	{
		float factor = (float) (frequency * (Math.PI * 2.0)) / rate;
		int[] sine = new int[datasize];
		for (int i = 0; i < datasize; i++)
		{
			int sample = (int) (((float) amp)*Math.sin((i+offset)*factor));
			sine[i] = sample;
		}
		return sine;
	}
}