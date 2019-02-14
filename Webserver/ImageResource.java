package com.shea.webserver;

import java.awt.AlphaComposite;
import java.awt.Color;
import java.awt.Composite;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.RenderingHints;
import java.awt.geom.AffineTransform;
import java.awt.geom.Ellipse2D;
import java.awt.image.AffineTransformOp;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.text.NumberFormat;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;

import javax.imageio.ImageIO;
import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Response;

import com.jhlabs.image.EmbossFilter;
import com.jhlabs.image.GaussianFilter;
import com.shea.webserver.Fonts;

@Path("")
public class ImageResource {
	
	public static Random random = new Random();
	
	public static String getNewLinedText(String text, int charsPerLine) {
		int times = (int) Math.ceil(text.length()/(double) charsPerLine);
		int n = 0, m = charsPerLine;
		String newText = "";
		for (int i = 0; i < times; i++) {
			if (n != 0) {
				while (text.charAt(n) != ' ' && text.length() != n) {
					if (n != 0) {
						n -= 1;
					} else {
						n = ((i + 1) * charsPerLine) - charsPerLine;
		                break;
					}
				}
			}
			if (text.length() >= m) {
				while (text.charAt(m) != ' ' && text.length() != m) {
					if (m != 0) {
						m -= 1;
					} else {
						m = (i + 1) * charsPerLine;
		                break;
					}
				}
			}
			newText += text.substring(n, Math.min(text.length(), m)).trim() + "\n";
			n += charsPerLine;
			m += charsPerLine;
		}
		
		return newText;
	}
	
	public static String getNewLinedWidthText(Graphics2D graphics, Font font, String text, int maxWidth) {
		String[] splitText = text.trim().split(" ");
		String newText = "";
		int width = 0, n = 0;
		for (String word : splitText) {
			word += " ";
			int m = word.length();
			int textWidth = graphics.getFontMetrics(font).stringWidth(word);
			if (textWidth > maxWidth) {
			    while (true) {
			    	String cutWord = word.substring(n, m);
			    	int cutWordWidth = graphics.getFontMetrics(font).stringWidth(cutWord);
			    	if (cutWordWidth > maxWidth) {
			    	    m -= 1;
			    	} else {
			    		newText += cutWord + "\n";
			    		if (m == word.length()) {
			    			break;
			    		} else {
			    			n = m;
			    			m = word.length();
			    		}
			    	}
			    }
			} else {
				width += textWidth;
				if (width > maxWidth) {
					newText += "\n" + word;
					width = 0;
				} else {
					newText += word;
				}
			}
		} 
		
		return newText;
	}
	
	public static void drawText(Graphics2D graphics, String text, int x, int y) {
	    int lineHeight = graphics.getFontMetrics().getHeight();
	    
		String[] lines = text.split("\n");
		for(int lineCount = 0; lineCount < lines.length; lineCount++) {
		    graphics.drawString(lines[lineCount], x, y + lineCount * lineHeight);
		}
	}
	
	public static BufferedImage circlify(Image image) {
	    if(image.getHeight(null) != image.getWidth(null)) {
	        throw new IllegalArgumentException("Image width is not the same as the height");
	    }
	    
	    int width = image.getWidth(null);
	    
	    BufferedImage circleBuffer = new BufferedImage(width, width, BufferedImage.TYPE_INT_ARGB);
	    
	    Graphics2D graphics = circleBuffer.createGraphics();
		
	    graphics.setClip(new Ellipse2D.Float(0, 0, width, width));
	    graphics.drawImage(image, 0, 0, width, width, null);
	    
	    return circleBuffer;
	}
	
	public static BufferedImage rotate(BufferedImage image, double degrees) {
	    double angle = Math.toRadians(degrees);
	    double sin = Math.abs(Math.sin(angle)), cos = Math.abs(Math.cos(angle));
	    
	    int width = image.getWidth(), height = image.getHeight();
	    int newWidth = (int) Math.floor(width * cos + height *sin), newHeight = (int) Math.floor(height * cos + width * sin);
	    
	    BufferedImage result = new BufferedImage(newWidth, newHeight, BufferedImage.TYPE_INT_ARGB);
	    
	    Graphics2D graphics = result.createGraphics();
	    graphics.translate((newWidth - width) / 2, (newHeight - height) / 2);
	    graphics.rotate(angle, width / 2, height / 2);
	    graphics.drawRenderedImage(image, null);
	    graphics.dispose();
	    
	    return result;
	}
	
	public static BufferedImage asBufferedImage(Image image) {
	    BufferedImage bufferedImage = new BufferedImage(image.getWidth(null), image.getHeight(null), BufferedImage.TYPE_INT_ARGB);
	    Graphics2D graphics = bufferedImage.createGraphics();
	    graphics.drawImage(image, 0, 0, null);

	    return bufferedImage;
	}
	
	public static byte[] getImageBytes(BufferedImage image) throws IOException {
		ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
		ImageIO.write(image, "png", outputStream);
		return outputStream.toByteArray();
	}
	
	@GET
	@Path("/hot")
	@Produces({"image/png", "text/plain"})
	public Response getHotImage(@QueryParam("image") String query) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user/image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage background = new BufferedImage(419, 493, BufferedImage.TYPE_INT_ARGB);
		BufferedImage image = ImageIO.read(new File("thats-hot-meme.png"));
		Image resizedImage = image.getScaledInstance(419, 493, Image.SCALE_DEFAULT);
		Image resizedAvatar = avatar.getScaledInstance(400, 300, Image.SCALE_DEFAULT);
		
		Graphics graphics = background.getGraphics();
		graphics.drawImage(resizedAvatar, 8, 213, null);
		graphics.drawImage(resizedImage, 0, 0, null);
			
	    return Response.ok(getImageBytes(background)).build();
	}
	
	@GET
	@Path("/flag")
	@Produces({"image/png", "text/plain"})
	public Response getFlagImage(@QueryParam("image") String query, @QueryParam("flag") String flagQuery) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage flag;
		try {
			flag = ImageIO.read(new URL("http://www.geonames.org/flags/x/" + flagQuery + ".gif"));
		} catch (Exception e) {
			return Response.status(400).entity("Flag initial is invalid :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage image = new BufferedImage(200, 200, BufferedImage.TYPE_INT_ARGB);
		Image resizedAvatar = avatar.getScaledInstance(200, 200, Image.SCALE_DEFAULT);
		Image resizedFlag = flag.getScaledInstance(200, 200, Image.SCALE_DEFAULT);
		
		Graphics2D graphics = image.createGraphics();
		graphics.drawImage(resizedAvatar, 0, 0, null);
		Composite composite = AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.35F);
		graphics.setComposite(composite);
		graphics.drawImage(resizedFlag, 0, 0, null);
		
		return Response.ok(getImageBytes(image)).build();		
	}
	
	@GET
	@Path("/trash")
	@Produces({"image/png", "text/plain"})
	public Response getTrashImage(@QueryParam("image") String query) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user/image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage image = ImageIO.read(new File("trash-meme.jpg"));
		Image resizedAvatar = avatar.getScaledInstance(385, 384, Image.SCALE_DEFAULT);
		
		GaussianFilter filter = new GaussianFilter(20);
	    BufferedImage blurredAvatar = filter.filter(asBufferedImage(resizedAvatar), null);
	    
		Graphics graphics = image.getGraphics();
		graphics.drawImage(blurredAvatar, 384, 0, null);
		
		return Response.ok(getImageBytes(image)).build();	
	}
	
	@GET
	@Path("/www")
	@Produces({"image/png", "text/plain"})
	public Response getWhoWouldWinImage(@QueryParam("firstImage") String firstQuery, @QueryParam("secondImage") String secondQuery) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(firstQuery, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("First image/user is invalid :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage firstAvatar;
		try {
			firstAvatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The first url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		try {
			url = new URL(URLDecoder.decode(secondQuery, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Second image/user is invalid :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage secondAvatar;
		try {
			secondAvatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The second url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage image = ImageIO.read(new File("whowouldwin.png"));
		Image firstResizedAvatar = firstAvatar.getScaledInstance(400, 400, Image.SCALE_DEFAULT);
		Image secondResizedAvatar = secondAvatar.getScaledInstance(400, 400, Image.SCALE_DEFAULT);
	    
		Graphics graphics = image.getGraphics();
		graphics.drawImage(firstResizedAvatar, 30, 180, null);
		graphics.drawImage(secondResizedAvatar, 510, 180, null);
		
		return Response.ok(getImageBytes(image)).build();	
	}
	
	@GET
	@Path("/fear")
	@Produces({"image/png", "text/plain"})
	public Response getFearImage(@QueryParam("image") String query) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user/image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage image = ImageIO.read(new File("fear-meme.png"));
		Image resizedAvatar = avatar.getScaledInstance(251, 251, Image.SCALE_DEFAULT);
	    
		Graphics graphics = image.getGraphics();
		graphics.drawImage(resizedAvatar, 260, 517, null);
		
		return Response.ok(getImageBytes(image)).build();	
	}
	
	@GET
	@Path("/emboss")
	@Produces({"image/png", "text/plain"})
	public Response getEmbossImage(@QueryParam("image") String query) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user/image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		EmbossFilter filter = new EmbossFilter();
	    BufferedImage embossAvatar = filter.filter(avatar, null);
		
		return Response.ok(getImageBytes(embossAvatar)).build();	
	}
	
	@GET
	@Path("/ship")
	@Produces({"image/png", "text/plain"})
	public Response getShipImage(@QueryParam("firstImage") String firstQuery, @QueryParam("secondImage") String secondQuery) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(firstQuery, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("First user is invalid :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage firstAvatar;
		try {
			firstAvatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The first url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		try {
			url = new URL(URLDecoder.decode(secondQuery, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Second user is invalid :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage secondAvatar;
		try {
			secondAvatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The second url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage image = new BufferedImage(880, 280, BufferedImage.TYPE_INT_ARGB);
		BufferedImage heart = ImageIO.read(new File("heart.png"));
		Image firstResizedAvatar = firstAvatar.getScaledInstance(280, 280, Image.SCALE_DEFAULT);
		Image secondResizedAvatar = secondAvatar.getScaledInstance(280, 280, Image.SCALE_DEFAULT);
	    
		Graphics graphics = image.getGraphics();
		graphics.drawImage(firstResizedAvatar, 0, 0, null);
		graphics.drawImage(heart, 280, 0, null);
		graphics.drawImage(secondResizedAvatar, 600, 0, null);
		
		return Response.ok(getImageBytes(image)).build();	
	}
	
	@GET
	@Path("/vr")
	@Produces({"image/png", "text/plain"})
	public Response getVrImage(@QueryParam("image") String query) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user/image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage background = new BufferedImage(493, 511, BufferedImage.TYPE_INT_ARGB);
		BufferedImage image = ImageIO.read(new File("vr.png"));
		Image resizedImage = image.getScaledInstance(493, 511, Image.SCALE_DEFAULT);
		Image resizedAvatar = avatar.getScaledInstance(225, 150, Image.SCALE_DEFAULT);
	    
		Graphics graphics = background.getGraphics();
		graphics.drawImage(resizedAvatar, 15, 310, null);
		graphics.drawImage(resizedImage, 0, 0, null);
		
		return Response.ok(getImageBytes(background)).build();	
	}
	
	@GET
	@Path("/shit")
	@Produces({"image/png", "text/plain"})
	public Response getShitImage(@QueryParam("image") String query) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user/image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage background = new BufferedImage(763, 1080, BufferedImage.TYPE_INT_ARGB);
		BufferedImage image = ImageIO.read(new File("shit-meme.png"));
		avatar = asBufferedImage(avatar.getScaledInstance(192, 192, Image.SCALE_DEFAULT));
		
		AffineTransform transform = new AffineTransform();
	    transform.rotate(Math.toRadians(-50), avatar.getWidth()/2, avatar.getHeight()/2);
	    AffineTransformOp op = new AffineTransformOp(transform, AffineTransformOp.TYPE_BILINEAR);
	    avatar = op.filter(avatar, null);
	    
		Graphics graphics = background.getGraphics();
		graphics.drawImage(avatar, 240, 700, null);
		graphics.drawImage(image, 0, 0, null);
		
		return Response.ok(getImageBytes(background)).build();	
	}
	
	@GET
	@Path("/gay")
	@Produces({"image/png", "text/plain"})
	public Response getGayImage(@QueryParam("image") String query) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user/image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage image = ImageIO.read(new File("gay.png"));
		avatar = asBufferedImage(avatar.getScaledInstance(600, 600, Image.SCALE_DEFAULT));
	    
		Graphics graphics = avatar.getGraphics();
		graphics.drawImage(image, 0, 0, null);
		
		return Response.ok(getImageBytes(avatar)).build();	
	}
	
	@GET
	@Path("/beautiful")
	@Produces({"image/png", "text/plain"})
	public Response getBeautifulImage(@QueryParam("image") String query) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(query, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user/image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage image = ImageIO.read(new File("beautiful.png"));
		avatar = asBufferedImage(avatar.getScaledInstance(90, 104, Image.SCALE_DEFAULT));
		
		avatar = rotate(avatar, -1);
	    
		Graphics graphics = image.getGraphics();
		graphics.drawImage(avatar, 253, 25, null);
		graphics.drawImage(avatar, 256, 222, null);
		
		return Response.ok(getImageBytes(image)).build();	
	}
	
	@GET
	@Path("/discord")
	@Produces({"image/png", "text/plain"})
	public Response getDiscordImage(@QueryParam("text") String query, @QueryParam("theme") String theme, @QueryParam("name") String name, @QueryParam("colour") String colour, @QueryParam("bot") boolean bot, @QueryParam("image") String avatarUrl) throws Exception {
		URL url;
		try {
			url = new URL(URLDecoder.decode(avatarUrl, StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		BufferedImage avatar;
		try {
			avatar = ImageIO.read(url);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		avatar = circlify(avatar.getScaledInstance(100, 100, BufferedImage.TYPE_INT_ARGB));
		
		try {
			url = new URL(URLDecoder.decode("https://cdn.discordapp.com/emojis/441255212582174731.png", StandardCharsets.UTF_8));
		} catch (Exception e) {
			return Response.status(400).entity("Invalid emote :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		Image botImage;
		try {
			botImage = ImageIO.read(url).getScaledInstance(60, 60, Image.SCALE_DEFAULT);
		} catch (Exception e) {
			return Response.status(400).entity("The bot emote url is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		int breaks = query.trim().split("\n").length - 1; 
		
		int times = (int) Math.ceil(query.length()/50D);
		
	    int height = (breaks * 36) + (times * 36);
	    int length = bot ? 66 : 0;
		
	    String text = getNewLinedText(query, 50);
		
		Font mainText = Fonts.WHITNEY_BOOK.deriveFont(0, 34);
		Font nameText = Fonts.WHITNEY_MEDIUM.deriveFont(0, 40);
		Font timeText = Fonts.WHITNEY_LIGHT.deriveFont(0, 24);
		
		BufferedImage image = new BufferedImage(1000, 115 + height, BufferedImage.TYPE_INT_ARGB);
		Graphics2D graphics = image.createGraphics();
		
		RenderingHints hints = new RenderingHints(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
		graphics.setRenderingHints(hints);
		
		int nameWidth = graphics.getFontMetrics(nameText).stringWidth(name);
		int nameHeight = 40;
		
		graphics.setColor(theme.equals("dark") ? new Color(54, 57, 63) : Color.WHITE);
		graphics.fillRect(0, 0, image.getWidth(), image.getHeight());
		graphics.drawImage(avatar, 20, 10, null);
		if (bot) {
			graphics.drawImage(botImage, 170 + nameWidth, 2, null);
		}
		graphics.setColor(theme.equals("white") ? new Color(116, 127, 141) : Color.WHITE);
		graphics.setFont(mainText);
		drawText(graphics, text, 160, nameHeight + 54);
		graphics.setColor(Color.decode("#" + colour));
		graphics.setFont(nameText);
		graphics.drawString(name, 160, 6 + nameHeight);
		graphics.setColor(new Color(122, 125, 130));
		graphics.setFont(timeText);
		graphics.drawString("Today at " + LocalTime.now(ZoneOffset.UTC).format(DateTimeFormatter.ofPattern("HH:mm")), 170 + nameWidth + length, (nameHeight/2) - 2 + 24);
		
		return Response.ok(getImageBytes(image)).build();
	}
	
	@GET
	@Path("/trump")
	@Produces({"image/png", "text/plain"})
	public Response getTrumpImage(@QueryParam("text") String query) throws Exception {	
		String text = getNewLinedText(query, 70);
		
		Font textFont = new Font("Arial", 0, 25);
		
		BufferedImage image = ImageIO.read(new File("trumptweet-meme.png"));
		
		Graphics2D graphics = image.createGraphics();
		
		RenderingHints hints = new RenderingHints(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
		graphics.setRenderingHints(hints);
		
		graphics.setColor(Color.BLACK);
		graphics.setFont(textFont);
		drawText(graphics, text, 60, 150);
		
		return Response.ok(getImageBytes(image)).build();
	}
	
	@POST
	@Path("/tweet")
	@Consumes("application/json")
	@Produces({"image/png", "text/plain"})
	@SuppressWarnings("unchecked")
	public Response getTweetImage(Map<String, Object> body) throws Exception {
		String displayName = (String) body.get("displayName");
		String tagName = (String) body.get("name");
		String avatarUrl = (String) body.get("avatarUrl");
		List<String> likeAvatarUrls = (List<String>) body.get("urls");
		int likes = (int) body.get("likes");
		int retweets = (int) body.get("retweets");
		String text = (String) body.get("text");
		
		URL url;
		try {
			url = new URL(avatarUrl);
		} catch (Exception e) {
			return Response.status(400).entity("Invalid user :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		Image avatar;
		try {
			avatar = ImageIO.read(url).getScaledInstance(72, 72, Image.SCALE_DEFAULT);
		} catch (Exception e) {
			return Response.status(400).entity("The url given is not an image :no_entry:").header("Content-Type", "text/plain").build();
		}
		
		List<BufferedImage> likeAvatars = new ArrayList<>();
		for (String av : likeAvatarUrls) {
			try {
				url = new URL(av);
			} catch (Exception e) {
				return Response.status(400).entity("One of the random avatar urls is invalid :no_entry:").header("Content-Type", "text/plain").build();
			}
			
			try {
				likeAvatars.add(circlify(ImageIO.read(url).getScaledInstance(36, 36, Image.SCALE_DEFAULT)));
			} catch (Exception e) {
				likeAvatars.add(circlify(ImageIO.read(new URL("https://cdn.discordapp.com/embed/avatars/" + random.nextInt(5) + ".png")).getScaledInstance(36, 36, Image.SCALE_DEFAULT)));
			}
		}
		
		LocalDateTime time = LocalDateTime.now(ZoneOffset.UTC);
		
		BufferedImage image = ImageIO.read(new File("tweet.png"));
		
		Font nameFont = Fonts.GOTHAM_BLACK.deriveFont(0, 25);
		Font tagFont = Fonts.GOTHAM_BOOK.deriveFont(0, 20);
		Font likesFont = Fonts.GOTHAM_BOLD.deriveFont(Font.BOLD, 21);
		Font textFont = Fonts.SEGOE_UI.deriveFont(0, 25);
		
		Graphics2D graphics = image.createGraphics();
		
		RenderingHints hints = new RenderingHints(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
		graphics.setRenderingHints(hints);
		
		/* Maybe?
		PaintBrush brush = new PaintBrush(graphics);
		
		brush.image(circlify(avatar), 60, 44);
		
		brush.color(Color.BLACK)
			.font(nameFont)
			.text(displayName, 149, 72, false);
		
		brush.font(tagFont)
			.text("@" + tagName, 149, 102, false);
		
		brush.color(Color.BLACK)
			.font(textFont)
			.smartText(text.trim(), 60, 145, 884, false);
		
		String retweetsText = NumberFormat.getNumberInstance(Locale.UK).format(retweets);
		int retweetsWidth = graphics.getFontMetrics(likesFont).stringWidth(retweetsText);
		
		brush.font(likesFont)
			.text(retweetsText, 59, 342, false);
		
		int retweetTextWidth = graphics.getFontMetrics(tagFont).stringWidth("Retweets");
		
		brush.color(Color.GRAY)
			.font(tagFont)
			.text("Retweets", 64 + retweetsWidth, 342, false);
		
		String likesText = NumberFormat.getNumberInstance(Locale.UK).format(likes);
		int likesWidth = graphics.getFontMetrics(likesFont).stringWidth(likesText);
		
		brush.color(Color.BLACK)
			.font(likesFont)
			.text(likesText, 77 + retweetsWidth + retweetTextWidth, 342, false);
		
		brush.color(Color.GRAY)
			.font(tagFont)
			.text("Likes", 82 + retweetsWidth + retweetTextWidth + likesWidth, 342, false);
		
		brush.text(time.format(DateTimeFormatter.ofPattern("h:mm a")).toUpperCase() + time.format(DateTimeFormatter.ofPattern(" - dd LLL uuuu")), 60, 285, false);
		
		int additional = 0;
		for (BufferedImage likeAvatar : likeAvatars) {
			graphics.drawImage(likeAvatar, 398 + additional, 317, null);
			
			additional += 44;
		}
		*/
		
		graphics.setFont(textFont);

        String[] splitNewLineText = getNewLinedWidthText(graphics, textFont, text, 833).split("\n");
        int width = 60, height = 155;
        for (String newLine : splitNewLineText) {
            String[] splitText = newLine.split(" ");
            for (String word : splitText) {
                if (word.startsWith("#") || word.startsWith("@")) {
                    graphics.setColor(Color.decode("#0084b4"));
                    graphics.drawString(word + " ", width, height);
                } else {
                    graphics.setColor(Color.BLACK);
                    graphics.drawString(word + " ", width, height);
                }
                
                width += graphics.getFontMetrics(textFont).stringWidth(word + " ");
            }
            
            height += 30;
            width = 60;
        }
		
		graphics.drawImage(circlify(avatar), 60, 44, null);
		
		graphics.setColor(Color.BLACK);
		graphics.setFont(nameFont);
		graphics.drawString(displayName, 149, 72);
		graphics.setColor(Color.GRAY);
		graphics.setFont(tagFont);
		graphics.drawString("@" + tagName, 149, 102);
		graphics.setColor(Color.BLACK);
		graphics.setFont(likesFont);
		String retweetsText = NumberFormat.getNumberInstance(Locale.UK).format(retweets);
		graphics.drawString(retweetsText, 59, 342);
		int retweetsWidth = graphics.getFontMetrics(likesFont).stringWidth(retweetsText);
		graphics.setColor(Color.GRAY);
		graphics.setFont(tagFont);
		graphics.drawString("Retweets", 64 + retweetsWidth, 342);
		int retweetTextWidth = graphics.getFontMetrics(tagFont).stringWidth("Retweets");
		String likesText = NumberFormat.getNumberInstance(Locale.UK).format(likes);
		graphics.setColor(Color.BLACK);
		graphics.setFont(likesFont);
		graphics.drawString(likesText, 77 + retweetsWidth + retweetTextWidth, 342);
		int likesWidth = graphics.getFontMetrics(likesFont).stringWidth(likesText);
		graphics.setColor(Color.GRAY);
		graphics.setFont(tagFont);
		graphics.drawString("Likes", 82 + retweetsWidth + retweetTextWidth + likesWidth, 342);
		graphics.drawString(time.format(DateTimeFormatter.ofPattern("h:mm a")).toUpperCase() + time.format(DateTimeFormatter.ofPattern(" - dd LLL uuuu")), 60, 285);
		
		int additional = 0;
		for (BufferedImage likeAvatar : likeAvatars) {
			graphics.drawImage(likeAvatar, 398 + additional, 317, null);
			additional += 44;
		}
		
		return Response.ok(image).build();
	}
	
}
