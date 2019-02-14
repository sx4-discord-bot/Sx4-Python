package com.shea.webserver;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.ServerConnector;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.servlet.ServletContainer;

import com.shea.webserver.ImageResource;

public class Main {
	
	public static void main(String[] args) throws Exception {		
		ServletContextHandler contextHandler = new ServletContextHandler();
		contextHandler.setContextPath("/api");

		ResourceConfig resourceConfig = new ResourceConfig();
		resourceConfig.register(new ImageResource());

		ServletContainer container = new ServletContainer(resourceConfig);

		ServletHolder holder = new ServletHolder(container);
		holder.setAsyncSupported(true);

		contextHandler.addServlet(holder, "/*");

		Server server = new Server();

		ServerConnector connector = new ServerConnector(server);
		connector.setPort(8443);

		server.setHandler(contextHandler);
		server.addConnector(connector);

		server.start();
		server.join();
	}
}

