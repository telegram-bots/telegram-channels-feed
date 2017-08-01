package com.github.telegram_bots.channels_feed

import mu.KotlinLogging
import org.springframework.boot.ApplicationArguments
import org.springframework.boot.ApplicationRunner
import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.core.env.Environment

@SpringBootApplication
class ProcessorApplication(private val env: Environment) : ApplicationRunner {
    private val log = KotlinLogging.logger {}

    @Throws(Exception::class)
    override fun run(args: ApplicationArguments) {
        log.info { env }
    }

    companion object {
        @JvmStatic fun main(args: Array<String>) {
            SpringApplication.run(ProcessorApplication::class.java, *args)
        }
    }
}
